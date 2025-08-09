# import pytest
# from fastapi.testclient import TestClient
# from app.main import app
# from unittest.mock import patch

# client = TestClient(app)

# # simple mock text and answers
# SAMPLE_TEXT = "This is a test policy document. Grace period: thirty days. PED waiting period: 36 months."

# def fake_download_pdf(url, timeout=20):
#     # Return bytes that pypdf can't parse; we will patch extract_text to return SAMPLE_TEXT
#     return b"%PDF-FAKE-BYTES%"

# def fake_extract_text_from_pdf_bytes(b):
#     return SAMPLE_TEXT

# # @patch("app.services.pdf_loader.download_pdf", side_effect=fake_download_pdf)
# # @patch("app.services.pdf_loader.extract_text_from_pdf_bytes", side_effect=fake_extract_text_from_pdf_bytes)

# @patch("app.services.qa_pipeline.download_pdf", side_effect=fake_download_pdf)
# @patch("app.services.qa_pipeline.extract_text_from_pdf_bytes", side_effect=fake_extract_text_from_pdf_bytes)
# @patch("app.services.embedding_store._embed_text_openai")
# @patch("app.services.llm_service.generate_answer")
# def test_hackrx_run(mock_generate_answer, mock_embed, mock_extract, mock_download):
#     # Setup
#     mock_embed.return_value = [ [0.1]*1536 ]  # fake embedding vector(s)
#     # For generate_answer, return a canned reply
#     mock_generate_answer.return_value = "A grace period of thirty days is provided for premium payment."
#     headers = {"Authorization": "Bearer binary-brains", "Content-Type": "application/json"}
#     payload = {
#         "documents": "https://example.com/fake.pdf",
#         "questions": [
#             "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?"
#         ]
#     }

#     resp = client.post("/hackrx/run", json=payload, headers=headers)
#     assert resp.status_code == 200
#     data = resp.json()
#     assert "answers" in data
#     assert isinstance(data["answers"], list)
#     assert len(data["answers"]) == 1

import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch

client = TestClient(app)

SAMPLE_TEXT = "This is a test policy document. Grace period: thirty days. PED waiting period: 36 months."

def fake_download_pdf(url, timeout=20):
    return b"%PDF-FAKE-BYTES%"

def fake_extract_text_from_pdf_bytes(b):
    return SAMPLE_TEXT

@patch("app.services.qa_pipeline.download_pdf", side_effect=fake_download_pdf)
@patch("app.services.qa_pipeline.extract_text_from_pdf_bytes", side_effect=fake_extract_text_from_pdf_bytes)
@patch("app.services.embedding_store._embed_text_openai")
@patch("app.services.qa_pipeline.generate_answer")  # Patch where used!
def test_hackrx_run(mock_generate_answer, mock_embed, mock_extract, mock_download):
    mock_embed.return_value = [ [0.1]*1536 ]
    mock_generate_answer.return_value = "A grace period of thirty days is provided for premium payment."
    headers = {"Authorization": "Bearer binary-brains", "Content-Type": "application/json"}
    payload = {
        "documents": "https://example.com/fake.pdf",
        "questions": [
            "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?"
        ]
    }

    resp = client.post("/hackrx/run", json=payload, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "answers" in data
    assert isinstance(data["answers"], list)
    assert len(data["answers"]) == 1