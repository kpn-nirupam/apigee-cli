#!/usr/bin/env python
"""Source: https://apidocs.apigee.com/api/api-products-1

API Resource Path: /apiproducts
A list of URIs with an associated Quota (or "service plan"), which is used to expose customized API bundles to different developer groups.
API products enable you to bundle and distribute your APIs to multiple developer groups simultaneously, without having to modify code. An API product consists of a list of API resources (URIs) combined with a Service Plan (rate-limiting policy settings) plus any custom metadata required by the API provider. API products provide the basis for access control in Apigee, since they provide control over the set of API resources that apps are allowed to consume.

As part of the app provisioning workflow, developers select from a list of API products. This selection of an API product is usually made in the context of a developer portal. The developer app is provisioned with a key and secret (generated by and stored on Apigee Edge) that enable the app to access the URIs bundled in the selected API product. To access access API resources bundled in an API product, the app must present the API key issued by Apigee Edge. Apigee Edge will resolve the key that is presented against an API product, and then check associated  API resources and quota settings.

The API supports multiple API products per app key--your developers can consume multiple API products without requiring multiple keys. Also, a key can be 'promoted' from one API product to another. This enables you to promote developers from 'free' to 'premium' API products seamlessly and without user interruption.
"""

import json
import requests
from requests.exceptions import HTTPError

from apigee import APIGEE_ADMIN_API_URL
from apigee.abstract.api.apiproducts import IApiproducts, ApiproductsSerializer
from apigee.util import authorization

class Apiproducts(IApiproducts):

    def __init__(self, *args, **kwargs):
        """Apiproducts constructor

        Args:
            auth: Apigee Edge credentials object.
            org_name: Apigee Edge organization.
            apiproduct_name: API Product name.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)

    def create_api_product(self, request_body):
        """Create an API product: a list of API resources (URIs) combined with Quota settings that you can use to deliver customized API bundles to your developers.

        Args:
            request_body (str): JSON string.

        Returns:
            requests.Response()
        """
        uri = f'{APIGEE_ADMIN_API_URL}/v1/organizations/{self._org_name}/apiproducts'
        hdrs = authorization.set_header({'Accept': 'application/json',
                                         'Content-Type': 'application/json'},
                                        self._auth)
        body = json.loads(request_body)
        resp = requests.post(uri, headers=hdrs, json=body)
        resp.raise_for_status()
        return resp

    def delete_api_product(self):
        """Deletes an API Product

        Args:
            None

        Returns:
            requests.Response()
        """
        uri = f'{APIGEE_ADMIN_API_URL}/v1/organizations/{self._org_name}/apiproducts/{self._apiproduct_name}'
        hdrs = authorization.set_header({'Accept': 'application/json'},
                                        self._auth)
        resp = requests.delete(uri, headers=hdrs)
        resp.raise_for_status()
        return resp

    def get_api_product(self):
        """Gets an API Product

        Args:
            None

        Returns:
            requests.Response()
        """
        uri = f'{APIGEE_ADMIN_API_URL}/v1/organizations/{self._org_name}/apiproducts/{self._apiproduct_name}'
        hdrs = authorization.set_header({'Accept': 'application/json'},
                                        self._auth)
        resp = requests.get(uri, headers=hdrs)
        resp.raise_for_status()
        return resp

    def list_api_products(self, prefix=None, expand=False, count=1000, startkey=''):
        """Lists all API Products by name for an organization

        Args:
            prefix (str, optional): Filter results by a prefix string. Defaults to None.
            expand (bool, optional): If True, show product details. Defaults to False.
            count (int, optional): Apigee Edge for Public Cloud only:
                Number of API products to return in the API call.
                The maximum limit is 1000. Use with the startkey to provide more targeted filtering.
            startkey (str, optional): Apigee Edge for Public Cloud only:
                Returns a list of API products starting with the specified API product.
                For example, if you're returning 50 API products at a time (using the count query parameter),
                you can view products 50-99 by entering the name of the 50th API product in the first API.
                The API product name is case sensitive.

        Returns:
            requests.Response()
        """
        uri = f'{APIGEE_ADMIN_API_URL}/v1/organizations/{self._org_name}/apiproducts?expand={expand}&count={count}&startKey={startkey}'
        hdrs = authorization.set_header({'Accept': 'application/json'},
                                        self._auth)
        resp = requests.get(uri, headers=hdrs)
        resp.raise_for_status()
        return ApiproductsSerializer().serialize_details(resp, 'json', prefix=prefix)

    def update_api_product(self, request_body):
        """This method updates an existing API product

        Args:
            request_body (str): JSON string.

        Returns:
            requests.Response()
        """
        uri = f'{APIGEE_ADMIN_API_URL}/v1/organizations/{self._org_name}/apiproducts/{self._apiproduct_name}'
        hdrs = authorization.set_header({'Accept': 'application/json',
                                         'Content-Type': 'application/json'},
                                        self._auth)
        body = json.loads(request_body)
        resp = requests.put(uri, headers=hdrs, json=body)
        resp.raise_for_status()
        return resp

    def push_apiproducts(self, file):
        """Push API product file to Apigee

        This will create an API product if it does not exist and update if it does.

        Args:
            file (str): The file path.

        Returns:
            None

        Raises:
            HTTPError: If response status code is not successful or 404 (GET API Product).
        """
        with open(file) as f:
            body = f.read()

        apiproduct = json.loads(body)
        self._apiproduct_name = apiproduct['name']

        try:
            self.get_api_product()
            print('Updating', self._apiproduct_name)
            print(self.update_api_product(body).text)
        except HTTPError as e:
            if e.response.status_code == 404:
                print('Creating', self._apiproduct_name)
                print(self.create_api_product(body).text)
            else:
                raise e
