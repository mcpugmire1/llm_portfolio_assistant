#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { BackendStack } from '../lib/backend-stack';
import { FrontendStack } from '../lib/frontend-stack';
import { StorageStack } from '../lib/storage-stack';

const app = new cdk.App();

// Storage stack (S3 buckets)
const storageStack = new StorageStack(app, 'MattGPTStorageStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION || 'us-east-1',
  },
});

// Backend stack (Lambda + API Gateway)
const backendStack = new BackendStack(app, 'MattGPTBackendStack', {
  storiesBucket: storageStack.storiesBucket,
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION || 'us-east-1',
  },
});

// Frontend stack (S3 + CloudFront)
const frontendStack = new FrontendStack(app, 'MattGPTFrontendStack', {
  apiUrl: backendStack.apiUrl,
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION || 'us-east-1',
  },
});

app.synth();
