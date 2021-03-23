#
# ovirt-hosted-engine-ha -- ovirt hosted engine high availability
# Copyright (C) 2013 Red Hat, Inc.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
#

import os

from . import config
from . import config_constants
from . import constants

from ovirt_hosted_engine_ha.lib import util

from vdsm.client import ServerError


MOUNT_DIR = {
    "nfs": "",
    "nfs3": "",
    "nfs4": "",
    "posixfs": "",
    "glusterfs": "glusterSD"
}


def escape_remote_path(path):
    return path.replace("_", "__").replace("/", "_")


def canonize_file_path(storage_type, remote_path, sduuid):
    mount_dir = MOUNT_DIR[storage_type]
    escaped_path = escape_remote_path(remote_path)
    return os.path.join(
        constants.SD_MOUNT_PARENT,
        mount_dir,
        escaped_path,
        sduuid,
    )

def get_mount_target(config_):
    cli = util.connect_vdsm_json_rpc(
        logger=None,
        timeout=constants.VDSCLI_SSL_TIMEOUT
    )
    sd_uuid = config_.get(config.ENGINE, config_constants.SD_UUID)
    try:
        response = cli.StorageDomain.getInfo(storagedomainID=sd_uuid)
        return response['remotePath'],
    except (ServerError, KeyError):
        pass

def get_domain_path(config_):
    """
    Return path of storage domain holding engine vm
    """
    cli = util.connect_vdsm_json_rpc(
        logger=None,
        timeout=constants.VDSCLI_SSL_TIMEOUT
    )
    sd_uuid = config_.get(config.ENGINE, config_constants.SD_UUID)
    dom_type = config_.get(config.ENGINE, config_constants.DOMAIN_TYPE)
    parent = constants.SD_MOUNT_PARENT

    if dom_type in (
        constants.DOMAIN_TYPE_NFS,
        constants.DOMAIN_TYPE_NFS3,
        constants.DOMAIN_TYPE_NFS4,
        constants.DOMAIN_TYPE_POSIXFS,
        constants.DOMAIN_TYPE_GLUSTERFS,
    ):
        try:
            response = cli.StorageDomain.getInfo(storagedomainID=sd_uuid)
            path = canonize_file_path(
                dom_type,
                response['remotePath'],
                sd_uuid
            )
            if os.access(path, os.F_OK):
                return path

        except (ServerError, KeyError):
            # don't have remotePath? so fallback to old logic
            pass

    # fallback in case of getStorageDomainInfo call fails
    # please note that this code will get stuck if some of
    # the storage domains is not accessible rhbz#1140824
    if dom_type == constants.DOMAIN_TYPE_GLUSTERFS:
        parent = os.path.join(parent, constants.SD_GLUSTER_PREFIX)
    for dname in os.listdir(parent):
        path = os.path.join(parent, dname, sd_uuid)
        if os.access(path, os.F_OK):
            return path
    raise Exception("path to storage domain {0} not found in {1}"
                    .format(sd_uuid, parent))


def get_metadata_path(config_):
    """
    Return path to ha agent metadata
    """
    return os.path.join(get_domain_path(config_),
                        constants.SD_METADATA_DIR)
