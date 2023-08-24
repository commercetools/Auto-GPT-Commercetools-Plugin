from commercetools.platform.client import Client
from commercetools.platform.models.graph_ql import GraphQLRequest

import os

# Authorization credentials

class CT:
    def __init__(self):
        self.count = -1
        self.offset = 0
        self.project_key = os.environ["CTP_PROJECT_KEY"]
        self.client_id = os.environ["CTP_CLIENT_ID"]
        self.client_secret = os.environ["CTP_CLIENT_SECRET"]
        self.gen = None

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
        while True:   
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
        if (self.count < 0):
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
            if (self.count > 0):
                self.gen = self.get_one_order()

        if (self.count > 0):
            is_there_more = '\n Go to next step '
            if (self.count - 1 > self.offset):
                is_there_more = "\n Get the next order "
            return next(self.gen) + is_there_more

        return ''
