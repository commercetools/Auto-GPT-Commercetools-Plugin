import commercetools
from commercetools.platform.client import Client
from commercetools.platform.models.graph_ql import GraphQLRequest
from autogpt.processing.text import chunk_content, split_text, summarize_text
from autogpt.config import ConfigBuilder
import json
from autogpt.logs import logger

import os

# Authorization credentials

class CT:
    def __init__(self):
        self.count = -1
        self.offset = 0
        self.project_key = os.environ["CTP_PROJECT_KEY"]
        self.client_id = os.environ["CTP_CLIENT_ID"]
        self.client_secret = os.environ["CTP_CLIENT_SECRET"]

        # SDK settings
        self.auth_url = os.environ["CTP_AUTH_URL"]
        self.api_url = os.environ["CTP_API_URL"]
        self.scope = os.environ["CTP_SCOPES"]

        self.client = Client(
                client_id=self.client_id,
                client_secret=self.client_secret,
                scope=self.scope,
                url=self.api_url,
                token_url=self.auth_url,
            )

        self.gen = None

    def ct_execute_graph_ql(self, query):

        body = GraphQLRequest(query=query)

        result = self.client.with_project_key(project_key=self.project_key).graphql().post(body=body)
        return result

    def ct_get_products_info(self, skus, currency):
        sku_array = str(skus).replace("'", '"')

        query = f"""
            query {{
                products(skus: {sku_array}) {{
                    results {{
                        masterData {{
                            current {{
                                name(locale: "en-US")
                                masterVariant {{
                                sku
                                }}
                            }}
                        }}
                    }}
                }}
            }}
            """
        body = GraphQLRequest(query=query)

        result = self.client.with_project_key(project_key=self.project_key).graphql().post(body=body)
        return result

    def get_one_order (self):
        logger.info('Running get one order ****', str(self.offset))
        
        while True:   
            logger.info('In while true')
            n = self.offset
            query = f"""
                query {{
                    orders (limit: 1, offset: {n}) {{
                        results {{
                            lineItems {{
                                quantity
                                totalPrice {{
                                    centAmount
                                }}
                                variant {{
                                    sku
                                }}
                            }}
                        }}
                    }}
                }}
                """
            body = GraphQLRequest(query=query)

            result = self.client.with_project_key(project_key=self.project_key).graphql().post(body=body)
            yield result
            self.offset += 1

    def ct_get_all_orders(self):
        logger.info('----run')
        if (self.count < 0):
            logger.info('count -1')
            query = """
                query {
                    orders {
                        count
                    }
                }
                """
            body = GraphQLRequest(query=query)

            result = self.client.with_project_key(project_key=self.project_key).graphql().post(body=body)
            self.count = result.data['orders']['count']
            logger.info('count is' + str(self.count))
            if (self.count > 0):
                logger.info('setting gen')
                self.gen = self.get_one_order()

        if (self.count > 0):
            logger.info('On else >> '+ str(self.count))
            return next(self.gen)

        return ''
