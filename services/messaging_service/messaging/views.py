from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from .mongo import messages_collection
from datetime import datetime, timezone
from rest_framework.response import Response
from rest_framework import status
from bson import ObjectId


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

        message = {
            'sender_id': data.get('sender_id'),
            'sender_name': data.get('sender_name'),
            'group_id': data.get('group_id'),
            'content': data.get('content'),
            'file': str(data.get('file')) if data.get('file') else None,
            'status': 'sent',
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
        # PyMongo adds '_id' to the 'message' dict here
        messages_collection.insert_one(message)

        # Use your helper to clean the modified 'message' dict
        return Response(serialize_doc(message), status=status.HTTP_201_CREATED)
