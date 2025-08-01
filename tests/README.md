# Testing Strategy

This directory contains comprehensive tests for the Steam Wrapped application.

## Test Coverage

### ✅ Completed Tests (54 tests passing)

1. **Models** (`src/models/game.py`) - 100% coverage
   - Game creation with various data combinations
   - Property calculations (playtime in hours)
   - Steam API data parsing
   - Object equality and inequality

2. **Configuration** (`config.py`) - 100% coverage
   - Environment variable loading and validation
   - Font file validation
   - Error handling for missing configuration
   - Logging setup

3. **Display Service** (`src/ui/display.py`) - 100% coverage
   - Table generation and formatting
   - Summary display with time calculations
   - Error and success message display
   - Service factory function

4. **Steam API Service** (`src/services/steam_api.py`) - 100% coverage
   - HTTP client interactions
   - API response parsing and error handling
   - Context manager functionality
   - Game filtering and sorting
   - Factory function with validation

5. **Main Application** (`main.py`) - Integration tests
   - Successful execution flow
   - Error handling for various scenarios
   - Service integration
   - Exit code validation

### 📊 Coverage Summary

- **Total Coverage**: 49% (139/271 lines)
- **Tested Modules**: 5/7 modules
- **Tests Passing**: 54/54

### 🔄 Remaining Modules

- **Image Service** (`src/services/image_service.py`) - 16% coverage
  - Complex image generation with Pillow
  - Graphics rendering and layout
  - File I/O operations
  - Would require image generation testing (complex)

## Running Tests

```bash
# Run all tests
pdm run pytest tests/ -v

# Run specific test file
pdm run pytest tests/test_models.py -v

# Run with coverage report
pdm run pytest tests/ --cov=src --cov-report=html

# Run only unit tests (exclude integration)
pdm run pytest tests/ -m "not integration"
```

## Test Structure

- `test_models.py` - Data model tests
- `test_config.py` - Configuration and validation tests
- `test_display.py` - UI display service tests
- `test_steam_api.py` - HTTP API service tests
- `test_main.py` - Integration tests for main application

## Testing Approach

1. **Unit Tests**: Test individual components in isolation
2. **Mocking**: Use mocks for external dependencies (HTTP, file I/O)
3. **Error Handling**: Test both success and failure scenarios
4. **Edge Cases**: Test boundary conditions and error states
5. **Integration Tests**: Test component interactions

## Future Improvements

- Add tests for Image Service (requires image generation testing)
- Add performance tests for large datasets
- Add property-based testing with hypothesis
- Add API contract tests for Steam API