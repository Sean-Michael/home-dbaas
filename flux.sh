#!/bin/bash

kubectl create namespace flux-system


kubectl apply -f https://raw.githubusercontent.com/fluxcd/helm-operator/master/deploy/crds.yaml
kubectl apply -f https://raw.githubusercontent.com/fluxcd/helm-operator/master/deploy/flux-helm-release-crd.yaml

helm repo add fluxcd https://charts.fluxcd.io
helm upgrade -i helm-operator fluxcd/helm-operator \
  --namespace flux-system \
  --set helm.versions=v3