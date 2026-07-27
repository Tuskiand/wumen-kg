"""Backend app package.

Keep package import side-effect free so unit tests can import modules
without eagerly pulling in the FastAPI app and database setup.
"""

__all__: list[str] = []
