import os

from dotenv import load_dotenv
from flask import Blueprint, request

from blueprints.rrl.apis import require_api_key
from utils.main import get_fare_estimate_v2, get_fare_options_v2

load_dotenv()

API_KEY = os.getenv('x-api-key')
gtfs_zip_path = os.getenv('gtfs_zip_path')
gtfs_single_zip_path = os.getenv('gtfs_single_zip_path')

rrl_v2_bp = Blueprint('rrl_v2', __name__)


@rrl_v2_bp.route('/fare_estimate', endpoint='fare_estimate')
@require_api_key(API_KEY)
def fare_estimate():
    """Stop-to-stop fare between two stops on a route.
    ---
    tags: [fares]
    parameters:
      - name: route_id
        in: query
        type: string
        required: true
        description: Route id (metro 1-34, coach 1001-1040)
        example: "1"
      - name: start_idx
        in: query
        type: integer
        required: true
        description: Merged stop_id of the origin
        example: 1
      - name: end_idx
        in: query
        type: integer
        required: true
        description: Merged stop_id of the destination
        example: 5
    responses:
      200:
        description: Fare for the origin-destination pair
        examples:
          application/json:
            status: success
            data:
              fare:
                nac:
                  basic: 20
                  toll: 0
                  total: 20
      200 (failed):
        description: Unknown route or stop pair - status=failed, fare=null
    """
    data = None
    if request.method == 'GET':
        data = request.values.to_dict()
    if data is not None:
        return get_fare_estimate_v2(data['route_id'].lower(), data['start_idx'], data.get('end_idx'), data.get('fare'))
    else:
        return {'status': 'failed', 'description': 'Wrong input'}, 400


@rrl_v2_bp.route('/fare_options', endpoint='fare_options')
@require_api_key(API_KEY)
def fare_options():
    """Fare segments from a start stop - grouped where the fare changes.
    ---
    tags: [fares]
    parameters:
      - name: route_id
        in: query
        type: string
        required: true
        example: "1"
      - name: start_idx
        in: query
        type: integer
        required: true
        description: Merged stop_id to travel from
        example: 1
    responses:
      200:
        description: Fare bands as stop-index ranges (flat fare = one band)
        examples:
          application/json:
            status: success
            data:
              nac:
                - start_stop_index: 2
                  end_stop_index: 16
                  basic_fare: 20
                  toll: 0
                  total_fare: 20
                  amount_payable_by_user: 20
                  discount_percentage: 0
      400:
        description: Unknown route or stop
    """
    data = None
    if request.method == 'GET':
        data = request.values.to_dict()
    if data is not None:
        return get_fare_options_v2(data['route_id'], data['start_idx'])
    else:
        return {'status': 'failed', 'description': 'Wrong input'}, 400