# -*- coding: utf-8 -*-
# import pytest
# from dev.load import load
# from iscc_registry.models import IsccIdModel
#
#
# @pytest.mark.django_db
# def test_index(client):
#     response = client.get("/", follow=True)
#     assert "Select ISCC-ID" in response.rendered_content
#
#
# @pytest.mark.django_db
# def test_resolver_bad_request(client):
#     respone = client.get("/notaniscc")
#     assert respone.status_code == 400  # Bad Request
#
#
# @pytest.mark.django_db
# def test_resovler_not_found(client):
#     response = client.get("/ISCC:MEAJU5AXCPOIOYFL")
#     assert response.status_code == 404  # Not Found
#     assert response.content == b"ISCC:MEAJU5AXCPOIOYFL not found."
#
#
# @pytest.mark.django_db
# def test_resolver_bad_request(client):
#     respone = client.get("/notaniscc")
#     assert respone.status_code == 400  # Bad Request
#
#
# @pytest.mark.django_db
# def test_resovler_not_found(client):
#     response = client.get("/ISCC:MEAJU5AXCPOIOYFL")
#     assert response.status_code == 404  # Not Found
#
#
# @pytest.mark.django_db
# def test_resolver_resovles_internal(client):
#     load(1)
#     iscc_obj = IsccIdModel.objects.all().first()
#     response = client.get(f"/{iscc_obj.iscc_id}", follow=True)
#     assert response.status_code == 200
#     assert response.redirect_chain == [
#         ("/registry/iscc_registry/isccidmodel/330445058337719994/change/", 302)
#     ]
#
#
# @pytest.mark.django_db
# def test_resolver_resovles_external(client):
#     load(1)
#     iscc_obj = IsccIdModel.objects.all().first()
#     iscc_obj.metadata = {"redirect": "https://craft.de"}
#     iscc_obj.save()
#     response = client.get(f"/{iscc_obj.iscc_id}", follow=True)
#     assert response.status_code == 200
#     assert response.redirect_chain == [
#         ("https://craft.de", 302),
#         ("/registry/iscc_registry/isccidmodel/", 302),
#     ]
