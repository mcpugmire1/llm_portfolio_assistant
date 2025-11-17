import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Construct } from 'constructs';
import * as path from 'path';

interface BackendStackProps extends cdk.StackProps {
  storiesBucket: s3.IBucket;
}

export class BackendStack extends cdk.Stack {
  public readonly apiUrl: string;

  constructor(scope: Construct, id: string, props: BackendStackProps) {
    super(scope, id, props);

    // Lambda function for RAG handler
    const ragHandler = new lambda.Function(this, 'RAGHandler', {
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: 'rag_handler.lambda_handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '../../backend/lambdas')),
      timeout: cdk.Duration.seconds(30),
      memorySize: 512,
      environment: {
        OPENAI_API_KEY: process.env.OPENAI_API_KEY || '',
        PINECONE_API_KEY: process.env.PINECONE_API_KEY || '',
        PINECONE_INDEX: process.env.PINECONE_INDEX || 'mattgpt',
        PINECONE_NAMESPACE: process.env.PINECONE_NAMESPACE || 'default',
        STORIES_BUCKET: props.storiesBucket.bucketName,
      },
    });

    // Grant Lambda permission to read from stories bucket
    props.storiesBucket.grantRead(ragHandler);

    // API Gateway
    const api = new apigateway.RestApi(this, 'MattGPTAPI', {
      restApiName: 'MattGPT API',
      description: 'API for MattGPT RAG queries',
      defaultCorsPreflightOptions: {
        allowOrigins: apigateway.Cors.ALL_ORIGINS,
        allowMethods: apigateway.Cors.ALL_METHODS,
        allowHeaders: ['Content-Type', 'Authorization'],
      },
    });

    // /ask endpoint
    const askResource = api.root.addResource('ask');
    askResource.addMethod('POST', new apigateway.LambdaIntegration(ragHandler));

    // Store API URL
    this.apiUrl = api.url;

    // Outputs
    new cdk.CfnOutput(this, 'APIEndpoint', {
      value: api.url,
      description: 'API Gateway endpoint URL',
    });

    new cdk.CfnOutput(this, 'RAGHandlerArn', {
      value: ragHandler.functionArn,
      description: 'RAG Lambda function ARN',
    });
  }
}
