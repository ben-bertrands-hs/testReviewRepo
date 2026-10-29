#!/bin/sh
curl -X POST -H "Authorization: Bearer $DEPLOY_TOKEN" "https://deploy.example.com/notes?ref=$GITHUB_SHA"
