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
from . import constants


def get_domain_path(config_):
    """
    Return path of storage domain holding engine vm
    """
    sd_uuid = config_.get(config.ENGINE, config.SD_UUID)
    parent = constants.SD_MOUNT_PARENT
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