# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making BK-CI 蓝鲸持续集成平台 available.

Copyright (C) 2019 THL A29 Limited, a Tencent company.  All rights reserved.

BK-CI 蓝鲸持续集成平台 is licensed under the MIT license.

A copy of the MIT License is included in this file.


Terms of the MIT License:
---------------------------------------------------
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of
the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from __future__ import absolute_import, print_function, unicode_literals

import json

import python_atom_sdk
import requests


rpool = requests.Session()


class APIError(Exception):
    pass


def get_apigw_host():
    # 蓝鲸外部版本 APIGW 地址, 请填写安装环境的 BK_PAAS_INNER_HOST 环境变量
    BK_PAAS_INNER_HOST = python_atom_sdk.get_sensitive_conf("BK_PAAS_INNER_HOST")
    if BK_PAAS_INNER_HOST:
        host = "{BK_PAAS_INNER_HOST}/api/apigw/bcs-app/prod/apis/metrics/".format(
            BK_PAAS_INNER_HOST=BK_PAAS_INNER_HOST
        )
        return host

    # BCS 独立域名 地址
    BCS_APP_HOST = python_atom_sdk.get_sensitive_conf("BCS_APP_HOST")
    if BCS_APP_HOST:
        host = "{BCS_APP_HOST}/prod/apis/metrics/".format(BCS_APP_HOST=BCS_APP_HOST)
        return host

    raise APIError("私有配置变量 BK_PAAS_INNER_HOST 和 BCS_APP_HOST 不能同时为空")


def get_servicemonitor(cluster_id, namespace, name):
    project_code = python_atom_sdk.get_project_name()

    url = "{host}projects/{project_code}/clusters/{cluster_id}/servicemonitors/{namespace}/{name}/".format(
        host=get_apigw_host(),
        project_code=project_code,
        cluster_id=cluster_id,
        namespace=namespace,
        name=name,
    )

    params = {
        "app_code": python_atom_sdk.get_sensitive_conf("app_code"),
        "app_secret": python_atom_sdk.get_sensitive_conf("app_secret"),
    }
    headers = {
        "X-Tenant-Project-Code": project_code,
        "X-Operator": python_atom_sdk.get_pipeline_start_user_name(),
    }

    result = rpool.get(url, params=params, headers=headers).json()
    if result.get("code") == 0:
        return True
    return False


def update_servicemonitor(cluster_id, namespace, name, spec):
    project_code = python_atom_sdk.get_project_name()

    url = "{host}projects/{project_code}/clusters/{cluster_id}/servicemonitors/{namespace}/{name}/".format(
        host=get_apigw_host(),
        project_code=project_code,
        cluster_id=cluster_id,
        namespace=namespace,
        name=name,
    )
    params = {
        "app_code": python_atom_sdk.get_sensitive_conf("app_code"),
        "app_secret": python_atom_sdk.get_sensitive_conf("app_secret"),
    }
    headers = {
        "X-Tenant-Project-Code": python_atom_sdk.get_project_name(),
        "X-Operator": python_atom_sdk.get_pipeline_start_user_name(),
    }

    result = rpool.put(url, json=spec, params=params, headers=headers).json()

    if result.get("code") != 0:
        raise APIError(
            "update_servicemonitor result code %s != 0, message: %s, request_id: %s"
            % (result.get("code"), result.get("message"), result.get("request_id"))
        )


def create_servicemonitor(cluster_id, spec):
    project_code = python_atom_sdk.get_project_name()

    url = "{host}projects/{project_code}/clusters/{cluster_id}/servicemonitors/".format(
        host=get_apigw_host(), project_code=project_code, cluster_id=cluster_id
    )

    params = {
        "app_code": python_atom_sdk.get_sensitive_conf("app_code"),
        "app_secret": python_atom_sdk.get_sensitive_conf("app_secret"),
    }
    headers = {
        "X-Tenant-Project-Code": project_code,
        "X-Operator": python_atom_sdk.get_pipeline_start_user_name(),
    }

    result = rpool.post(url, json=spec, params=params, headers=headers).json()

    if result.get("code") != 0:
        raise APIError(
            "create_servicemonitor result code %s != 0, message: %s, request_id: %s"
            % (result.get("code"), result.get("message"), result.get("request_id"))
        )


def apply_serviemonitor(name, cluster_id, namespace, spec):
    """变更metrics"""
    if get_servicemonitor(cluster_id, namespace, name):
        python_atom_sdk.log.info("servicemonitor [%s] already exist, will update" % name)
        update_servicemonitor(cluster_id, namespace, name, spec)
        python_atom_sdk.log.info("servicemonitor [%s] update success" % name)
        return

    python_atom_sdk.log.info("servicemonitor [%s] not exist, will create" % name)
    create_servicemonitor(cluster_id, spec)
    python_atom_sdk.log.info("servicemonitor [%s] create success" % name)


def executor():
    """变更屏蔽"""
    python_atom_sdk.log.debug("start apply servicemonitor")

    # 输入
    input_params = python_atom_sdk.get_input()

    name = input_params.get("name")
    namespace = input_params.get("namespace")
    cluster_id = input_params.get("cluster_id")
    # python_atom_sdk.log.debug("selector: %s, %s" % (type(input_params.get("selector")), input_params.get("selector"))) # noqa
    # python_atom_sdk.log.debug("params: %s, %s" % (type(input_params.get("params")), input_params.get("params")))
    _selector = json.loads(input_params.get("selector", "[]"))
    _params = json.loads(input_params.get("params", "[]"))
    selector = {}
    # python_atom_sdk.log.debug("params : %s, %s, %s" % (input_params, _selector, _params))
    for i in _selector:
        if i["id"] != "labels":
            continue

        label_name = i["values"][0].get("value")
        label_value = i["values"][1].get("value")

        if label_name and label_value:
            selector[label_name] = label_value

    if len(selector) == 0:
        python_atom_sdk.log.error("关联的Labels不能为空")
        return 1

    params = {}
    for i in _params:
        if i["id"] != "params":
            continue

        key = i["values"][0].get("value")
        value = i["values"][1].get("value")
        if key and value:
            # value必须是list类型
            params[key] = [value]

    spec = {
        "port": input_params.get("port"),
        "name": name,
        "namespace": namespace,
        "service_name": input_params.get("service_name"),
        "sample_limit": int(input_params.get("sampleLimit") or "100000"),
        "interval": int(input_params.get("interval") or "30"),
        "selector": selector,
        "params": params,
        "path": input_params.get("path") or "/metrics",
        "cluster_id": cluster_id,
    }

    python_atom_sdk.log.debug("spec: %s" % spec)

    try:
        apply_serviemonitor(name, cluster_id, namespace, spec)
    except APIError as error:
        python_atom_sdk.log.error("apply servicemonitor failed, reason: %s", error)
        return 1
    except Exception as error:
        python_atom_sdk.log.error("apply servicemonitor error, %s", error)
        return 1

    python_atom_sdk.log.debug("finish")
    # output(success_count, failed_count)

    return 0


def main():
    code = executor()
    exit(code)


if __name__ == "__main__":
    main()
