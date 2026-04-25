from app.core.middleware import setup_cors


def test_setup_cors_adds_middleware():
    from fastapi import FastAPI
    
    app = FastAPI()
    setup_cors(app)
    
    assert len(app.user_middleware) == 1


def test_setup_cors_with_multiple_calls():
    from fastapi import FastAPI
    
    app = FastAPI()
    setup_cors(app)
    setup_cors(app)
    
    assert len(app.user_middleware) == 2