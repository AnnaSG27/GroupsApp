from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from .mongo import messages_collection
from datetime import datetime, timezone
from rest_framework.response import Response
from rest_framework import status
from bson import ObjectId
import boto3
import uuid
from django.conf import settings


def serialize_doc(doc):
    if isinstance(doc, dict):
        new_doc = {}
        for k, v in doc.items():
            if k == '_id':
                new_doc['id'] = str(v)
            else:
                new_doc[k] = serialize_doc(v)
        return new_doc
    elif isinstance(doc, list):
        return [serialize_doc(i) for i in doc]
    elif isinstance(doc, ObjectId):
        return str(doc)
    else:
        return doc
    
def upload_file_to_s3(file):
    s3 = boto3.client('s3')

    filename = f"{uuid.uuid4()}_{file.name}"

    s3.upload_fileobj(
        file,
        "groupsapp-files-jose-anna",
        filename,
        ExtraArgs={
            "ContentType": file.content_type
        }
    )

    file_url = f"https://groupsapp-files-jose-anna.s3.amazonaws.com/{filename}"

    return file_url


class MessageViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def list(self, request):
        group_id = request.query_params.get('group_id')

        query = {}
        if group_id:
            query['group_id'] = int(group_id)

        # 1. Fetch from MongoDB
        messages = list(messages_collection.find(query))

        # 2. Use your helper function to clean the data!
        # This replaces your manual loop and handles hidden BSON types.
        serialized_messages = serialize_doc(messages)

        return Response(serialized_messages)

    def create(self, request):
        data = request.data
        
        uploaded_file = request.FILES.get('file')

        file_url = None
        if uploaded_file:
            file_url = upload_file_to_s3(uploaded_file)

        message = {
            'sender_id': int(data.get('sender_id')),
            'sender_name': data.get('sender_name'),
            'group_id': int(data.get('group_id')),
            'content': data.get('content'),
            'file': file_url,
            'status': 'sent',
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
        # PyMongo adds '_id' to the 'message' dict here
        messages_collection.insert_one(message)

        # Use your helper to clean the modified 'message' dict
        return Response(serialize_doc(message), status=status.HTTP_201_CREATED)
