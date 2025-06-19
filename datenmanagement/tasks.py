from logging import getLogger
from typing import TYPE_CHECKING
from uuid import UUID

from django.apps import apps
from django_rq import enqueue
from laspy import open as laspy_open
from pyblisher import Bucket, Project, get_project, settings
from pyblisher.exceptions import ObjectNotFound

if TYPE_CHECKING:
  from httpx import Response

logger = getLogger(__name__)


def update_model(model_name, pk, attributes: dict):
  """
  Asynchronous updating of a model instance

  :param model_name: name of the model
  :param pk: primary key of the model instance
  :param attributes: dict of attributes, which should be updated
  :return:
  """
  logger.info('Run Task update_model')
  # get model
  model = apps.get_model(app_label='datenmanagement', model_name=model_name)

  try:
    # try to get instance of model
    instance = model.objects.get(pk=pk)

    # set new attribute values
    update_fields = []
    for attr, value in attributes.items():
      setattr(instance, attr, value)
      update_fields.append(attr)

    # save instance
    instance.save(update_fields=update_fields)

    # logging
    logger.info(f'Instance of {model_name} updated asynchronously.')
    logger.debug(f'Model {model_name} with pk {pk} updated asynchronously.')
  except model.DoesNotExist:
    logger.error(f'Model {model_name} with pk {pk} does not exist.')
  except Exception as e:
    logger.error(f'Update of Model {model_name} with pk {pk} failed: {str(e)}')


def send_pointcloud_to_vcpub(pk, dataset: UUID, path: str, objectkey: str):
  """
  asynchronous sending of a pointcloud to VC Publisher API

  :param pk: primary key of the pointcloud
  :param dataset: dataset id at VC Publisher
  :param path: path to uploaded file
  :param objectkey: filename as data bucket object key
  :return:
  """
  logger.debug('Run Task send_pointcloud_to_vcpub')

  # get needed constants
  model = apps.get_model(app_label='datenmanagement', model_name='Punktwolken')
  pointcloud = model.objects.get(pk=pk)
  pointcloud_projekt = pointcloud.projekt

  # VCP Project
  project: Project = get_project(id=settings.project_id)
  task_id = pointcloud_projekt.vcp_task_id

  # try to get bucket, if it doesn't exist create a new one and update task
  try:
    bucket: Bucket = project.get_bucket(
      id=pointcloud_projekt.vcp_dataset_bucket_id
    )
  except ObjectNotFound:
    logger.info('Bucket not found. Create new bucket.')
    # create new bucket
    bucket = project.create_bucket(name=pointcloud_projekt.bezeichnung)
    logger.debug('Bucket created.')
    print(bucket.__dict__)
    # update task
    bucket_reference = bucket.reference()
    parameters = {'dataset': bucket_reference}
    print(parameters)
    task = project.update_task(id=str(task_id), parameters=parameters)
    logger.debug('Task updated.')
    # update model
    update_model(
      model_name='Punktwolken_Projekte',
      pk=pointcloud_projekt.pk,
      attributes={'vcp_dataset_bucket_id': bucket._id},
    )

  response: Response = bucket.upload(key=f'/dataset/{objectkey}', path=path)
  match response.status_code:
    case 204:
      logger.debug('Pointcloud upload to VCPub was successful.')
      # delete local file
      import os

      os.remove(path)
      logger.debug(f'Local pointcloud file {path} deleted.')

      # update model asynchronously
      change_attr = {
        'vcp_object_key': objectkey,
      }
      enqueue(
        update_model, model_name='Punktwolken', pk=pk, attributes=change_attr
      )
    case _:
      logger.error(
        f'Pointcloud upload failed. {response.status_code}: {response.__dict__}'
      )


def calculate_2d_bounding_box_for_pointcloud(pk, path):
  """
  asynchronous calculation of 2D bounding box for pointcloud using laspy

  :param pk: pointcloud primary key
  :param path: path to pointcloud
  :return: 2D bounding box in WKT format
  """
  logger.info('Run Task calculate_2d_bounding_box_for_pointcloud')
  try:
    with laspy_open(path) as las_file:
      las = las_file.read()

      # extract x- and y-coordinates
      x_coords = las.x
      y_coords = las.y

      # get min/max values for x and y
      mn_x, mx_x = x_coords.min(), x_coords.max()
      mn_y, mx_y = y_coords.min(), y_coords.max()

      # create bounding box
      wkt = f'POLYGON(({mn_x} {mn_y}, {mx_x} {mn_y}, {mx_x} {mx_y}, {mn_x} {mx_y}, {mn_x} {mn_y}))'

      # update model
      enqueue(
        update_model,
        model_name='Punktwolken',
        pk=pk,
        attributes={'geometrie': wkt},
      )
  except Exception as e:
    logger.warning(
      f'Failed to calculate 2D bounding box for pointcloud with pk {pk}: {e}'
    )
