import laspy

from celery import shared_task
from django.apps import apps
from uuid import UUID

from datenwerft.celery import logger
from toolbox.vcpub.DataBucket import DataBucket


@shared_task
def send_pointcloud_to_vcpub(pk, dataset: UUID, path: str, filename: str):
  """
  Asynchronous sending of a pointcloud to the VCPub API.
  :param pk: primary key of the pointcloud
  :param dataset: dataset id at VCPublisher
  :param path: path to uploaded file
  :param filename: filename as data bucket key
  :return:
  """
  logger.info('Run Task send_pointcloud_to_vcpub')
  bucket = DataBucket(_id=str(dataset))
  with open(path, 'rb') as f:
    if filename:
      file = {filename: f}
    ok, key = bucket.upload(file=file)
    if ok:
      logger.debug('Pointcloud upload to VCPub was successful.')
      change_attr = {
        'vcp_object_key': key,
      }
      update_model(
        model_name='Punktwolken',
        pk=pk,
        attributes=change_attr
      )
      # Todo: delete locale pointcloud file
    else:
      logger.error('Pointcloud upload to VCPub failed. Try again later.')


@shared_task
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


@shared_task
def calculate_2d_bounding_box_for_pointcloud(pk, path):
  """
  Asynchronous calculation of 2D bounding box for pointcloud using laspy
  :param pk: pointcloud primary key
  :param path: path to pointcloud
  :return: 2d bounding box in WKT format
  """
  logger.info('Run Task calculate_2d_bounding_box_for_pointcloud')
  with laspy.open(path) as las_file:
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
    update_model(
      model_name='Punktwolken',
      pk=pk,
      attributes={'geometrie': wkt}
    )
