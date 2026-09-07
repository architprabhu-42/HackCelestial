from resilitrip.main import create_app


def test_openapi_has_documented_a1_operation_ids_and_discriminated_create_union() -> None:
    schema = create_app().openapi()
    expected = {
        "health_live", "health_ready", "list_scenarios", "create_trip", "get_trip",
        "replace_constraints", "replace_current_state", "apply_event", "generate_plans",
        "replace_active_itinerary", "get_plan", "adopt_plan", "reset_trip",
    }
    actual = {
        operation["operationId"]
        for path in schema["paths"].values()
        for operation in path.values()
        if isinstance(operation, dict) and "operationId" in operation
    }
    assert expected == actual
    request_schema = schema["paths"]["/api/v1/trips"]["post"]["requestBody"]["content"]["application/json"]["schema"]
    assert request_schema["anyOf"] or request_schema["oneOf"]


def test_openapi_has_all_required_discriminators_and_examples() -> None:
    schema = create_app().openapi()
    assert schema["components"]["schemas"]["EvidenceValue"]["discriminator"]["propertyName"] == "value_kind"
    event_content = schema["paths"]["/api/v1/trips/{trip_id}/events"]["post"]["requestBody"]["content"]["application/json"]
    assert event_content["schema"]["discriminator"]["propertyName"] == "type"
    request_examples = sum(
        len(operation.get("requestBody", {}).get("content", {}).get("application/json", {}).get("examples", {}))
        for path in schema["paths"].values() for operation in path.values() if isinstance(operation, dict)
    )
    response_examples = sum(
        len(response.get("content", {}).get("application/json", {}).get("examples", {}))
        for path in schema["paths"].values() for operation in path.values() if isinstance(operation, dict)
        for response in operation.get("responses", {}).values()
    )
    assert request_examples == 6
    assert response_examples == 2


def test_api26_through_api29_guarded_edit_contract_is_exact() -> None:
    schema = create_app().openapi()
    command = schema["components"]["schemas"]["ItineraryEditCommand"]
    assert set(command["properties"]) == {
        "expected_trip_version", "active_itinerary", "constraints",
        "acknowledge_hard_changes", "provenance",
    }
    assert set(command["required"]) == set(command["properties"])
    assert command["additionalProperties"] is False
    operation = schema["paths"]["/api/v1/trips/{trip_id}/itinerary"]["put"]
    assert operation["operationId"] == "replace_active_itinerary"
    assert "200" in operation["responses"]
    mutation_values = schema["components"]["schemas"]["MutationResponse"]["properties"]["mutation_kind"]["enum"]
    assert "itinerary_edit" in mutation_values and "itinerary" not in mutation_values
    actions = schema["components"]["schemas"]["AvailableActions"]
    assert "can_edit_itinerary" in actions["properties"]
    error_values = set(schema["components"]["schemas"]["ApiErrorCode"]["enum"])
    assert {"ITINERARY_EDIT_INVALID", "COMPLETED_ACTIVITY_IMMUTABLE",
        "ACTIVE_ACTIVITY_IMMUTABLE", "HARD_CHANGE_ACKNOWLEDGEMENT_REQUIRED"} <= error_values
