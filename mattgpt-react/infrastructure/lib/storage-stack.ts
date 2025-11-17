import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import { Construct } from 'constructs';

export class StorageStack extends cdk.Stack {
  public readonly storiesBucket: s3.Bucket;

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // S3 bucket for stories data (JSONL files)
    this.storiesBucket = new s3.Bucket(this, 'StoriesBucket', {
      bucketName: `mattgpt-stories-${this.account}`,
      versioned: false,
      encryption: s3.BucketEncryption.S3_MANAGED,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
      autoDeleteObjects: false,
    });

    // Output bucket name
    new cdk.CfnOutput(this, 'StoriesBucketName', {
      value: this.storiesBucket.bucketName,
      description: 'S3 bucket for stories JSONL data',
    });
  }
}
