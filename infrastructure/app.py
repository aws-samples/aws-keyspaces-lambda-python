#!/usr/bin/env python3
import os
from aws_cdk import core
from app_stack import AppStack

app = core.App()
AppStack(app, 'cassandra-demo')
app.synth()
