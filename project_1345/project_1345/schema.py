from drf_spectacular.openapi import AutoSchema


METHOD_WITH_INDEX = ["GET", "PATCH", "DELETE"]
METHOD_WITHOUT_INDEX = ["GET", "POST", "PUT"]


def custom_preprocessing_hook(endpoints):
    # print("custom_preprocessing_hook")
    filtered = []
    for path, path_regex, method, callback in endpoints:
        # Check if the path includes a `pk` (primary key) in the URL
        is_index = "<" in path_regex
        if method in METHOD_WITH_INDEX:
            if is_index:
                filtered.append((path, path_regex, method, callback))
        if method in METHOD_WITHOUT_INDEX:
            if not is_index:
                filtered.append((path, path_regex, method, callback))

    return filtered


class CustomAutoSchema(AutoSchema):
    METHOD_WITH_INDEX = ["GET", "PATCH", "DELETE"]
    METHOD_WITHOUT_INDEX = ["GET", "POST", "PUT"]
    METHOD_RESET_PARAMETERS = ["GET"]

    def get_operation_id(self):
        # print(f"++++ Global CustomAutoSchema get_operation_id {self.path_regex}")

        # Call the parent method to get the default operation ID
        o_id = super().get_operation_id()

        # Check if the path includes parameters (e.g., `<pk>`)
        if "<" in self.path_regex:
            # Modify the operation ID for detail views
            return f"{o_id}_detail"

        # Return the default or modified operation ID for list views
        return f"{o_id}_list"

    def get_operation(self, *args, **kwargs):
        # Call the base implementation
        operation = super().get_operation(*args, **kwargs)
        if operation is None:
            return None
        method = args[3]
        # print(f"get_operation {method}")
        # Check for DELETE method and operation_id ending with `_list`
        is_index = operation.get("operationId", "").endswith("_detail")
        if is_index:
            self._tune_index_parameters(operation, method)
        if method in self.METHOD_WITH_INDEX and is_index:
            return operation
        if method in self.METHOD_WITHOUT_INDEX and not is_index:
            return operation
        return None

    def _tune_index_parameters(self, operation: dict, method: str):
        is_parameters = "parameters" in operation
        if is_parameters and method in self.METHOD_RESET_PARAMETERS:
            # Remove search and filter if pk is in the URL (detail view)
            fileter_name = ["id", "product_id"]
            new_parameters = []
            for param in operation["parameters"]:
                if param.get("name") in fileter_name:
                    new_parameters.append(param)
            operation["parameters"] = new_parameters
        return operation
