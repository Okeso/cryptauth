# Testing with Traefik

Launch a test instance of Traefik on port `8888` with the following command: 

```shell
traefik --configFile=traefik.yml
```

The authentication service is exposed via:

- [http://auth.test.localhost:8888/](http://auth.test.localhost:8888/)

A test service is available and forwards to http://example.org via:

- [http://service.test.localhost:8888/](http://service.test.localhost:8888/)

