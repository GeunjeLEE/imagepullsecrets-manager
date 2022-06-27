# prs-manager
Private registry secret manager in kubernetes

## docker build
docker build --tag nigasa12/prs-manager:0.1 .
docker push nigasa12/prs-manager:0.1

## helm
> cd prs-manager

helm install prs-manager -f values.yaml ./helm<br>
helm upgrade prs-manager -f values.yaml ./helm<br>