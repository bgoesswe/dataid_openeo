""" Initialize the Gateway """

from .gateway import Gateway

gateway = Gateway()
gateway.set_cors()

# Get application context and map RPCs to endpoints
ctx, rpc = gateway.get_rpc_context()
with ctx:
    gateway.add_endpoint("/collections", func=rpc.data.get_all_products, auth=False, validate=True)
    gateway.add_endpoint("/collections/<name>", func=rpc.data.get_product_detail, auth=False, validate=True)
    gateway.add_endpoint("/collections/<name>/result", func=rpc.data.get_product_detail_filelist, auth=False, validate=True)
    gateway.add_endpoint("/collections/<name>/updatedresult", func=rpc.data.get_product_detail_filelist_updated, auth=False,
                         validate=True)
    gateway.add_endpoint("/collections/<name>/records", func=rpc.data.get_records, auth=True, validate=True)
    gateway.add_endpoint("/processes", func=rpc.processes.get_all, auth=True, validate=True)
    gateway.add_endpoint("/processes", func=rpc.processes.create, auth=True, validate=True, methods=["POST"], role="admin")
    gateway.add_endpoint("/process_graphs", func=rpc.process_graphs.get_all, auth=True, validate=True)
    gateway.add_endpoint("/process_graphs", func=rpc.process_graphs.create, auth=True, validate=True, methods=["POST"])
    gateway.add_endpoint("/process_graphs/<process_graph_id>", func=rpc.process_graphs.get, auth=True, validate=True)
    gateway.add_endpoint("/process_graphs/<process_graph_id>", func=rpc.process_graphs.modify, auth=True, validate=True, methods=["PATCH"])
    gateway.add_endpoint("/process_graphs/<process_graph_id>", func=rpc.process_graphs.delete, auth=True, validate=True, methods=["DELETE"])
    gateway.add_endpoint("/validation", func=rpc.process_graphs.validate, auth=True, validate=True, methods=["POST"])
    gateway.add_endpoint("/jobs", func=rpc.jobs.get_all, auth=True, validate=True)
    gateway.add_endpoint("/jobs", func=rpc.jobs.create, auth=True, validate=True, methods=["POST"])
    gateway.add_endpoint("/jobs/<job_id>", func=rpc.jobs.get, auth=True, validate=True)
    gateway.add_endpoint("/jobs/<job_id>", func=rpc.jobs.delete, auth=True, validate=True, methods=["DELETE"])
    gateway.add_endpoint("/jobs/<job_id>", func=rpc.jobs.modify, auth=True, validate=True, methods=["PATCH"])
    gateway.add_endpoint("/jobs/<job_id>/results", func=rpc.jobs.get_results, auth=True, validate=True)
    gateway.add_endpoint("/jobs/<job_id>/results", func=rpc.jobs.process, auth=True, validate=True, methods=["POST"], is_async=True)
    gateway.add_endpoint("/jobs/<job_id>/results", func=rpc.jobs.cancel_processing, auth=True, validate=True, methods=["DELETE"])
    # Additional endpoints
    gateway.add_endpoint("/version", func=rpc.jobs.version_current, auth=False, validate=False)
    gateway.add_endpoint("/version/<timestamp>", func=rpc.jobs.version, auth=False, validate=False)
    gateway.add_endpoint("/resetjobsdb", func=rpc.jobs.resetdb, auth=False, validate=False)
    gateway.add_endpoint("/resetpgdb", func=rpc.processes.resetdb, auth=False, validate=False)
    gateway.add_endpoint("/updaterecord", func=rpc.process_graphs.updaterecord, auth=True, validate=True, methods=["POST"])
    #gateway.add_endpoint("/updaterecord", func=rpc.data.updaterecord, auth=False, validate=False, methods=["POST"])
    gateway.add_endpoint("/updatestate", func=rpc.data.updatestate, auth=False, validate=False)
    #gateway.add_endpoint("/jobs/<job_id>/diff", func=rpc.jobs.diff, auth=True, validate=False)
    #gateway.add_endpoint("/jobs/<job_id>/diff", func=rpc.jobs.diff, auth=True, validate=False, methods=["POST"])
    gateway.add_endpoint("/updatebackend", func=rpc.jobs.updatebackend, auth=True, validate=True,
                         methods=["POST"])



# Validate if the gateway was setup as defined by the OpenAPI specification
gateway.validate_api_setup()
