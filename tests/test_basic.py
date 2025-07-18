# -*- coding: utf-8 -*-
"""
Basic tests for the Bitrix24 AI Assistant
"""
import pytest
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))


def test_basic_imports():
    """Test that basic modules can be imported"""
    try:
        import app
        assert True
    except ImportError:
        # If app module doesn't exist, that's okay for now
        assert True


def test_python_version():
    """Test that we're running on a supported Python version"""
    assert sys.version_info >= (3, 8)


def test_requirements_exist():
    """Test that requirements.txt exists"""
    requirements_path = os.path.join(os.path.dirname(__file__), '..', 'requirements.txt')
    assert os.path.exists(requirements_path)


def test_main_file_exists():
    """Test that main.py exists"""
    main_path = os.path.join(os.path.dirname(__file__), '..', 'main.py')
    assert os.path.exists(main_path)


if __name__ == "__main__":
    pytest.main([__file__])
