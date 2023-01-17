import sys
from google.api_core.client_options import ClientOptions
from google.cloud import automl_v1
from google.cloud.automl_v1.proto import service_pb2

class Score:
    def __init__(self):
        self.model = 'projects/919577446005/locations/us-central1/models/TST2565505874252529664'

    def __inline_text_payload(self, content): #content was file_path
        return {'text_snippet': {'content': content, 'mime_type': 'text/plain'} }

    def get_prediction(self, phrase):
        options = ClientOptions(api_endpoint='automl.googleapis.com')
        prediction_client = automl_v1.PredictionServiceClient(client_options=options)
        payload = self.__inline_text_payload(phrase)
        params = {}
        request = prediction_client.predict(self.model, payload, params) #phrase wass payload
        score = 0
        for annotation_payload in request.payload:
            score = annotation_payload.text_sentiment.sentiment
        return score  # waits until request is returned
