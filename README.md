# Rails bundle

### Auto build Rails environment in docker

* Require [Docker](https://docs.docker.com/install/)
* Require [Docker-bundle](https://github.com/docker-bundle/docker-bundle)  or [Docker-bundle-wrapper](https://github.com/docker-bundle/docker-bundle-wrapper)

## Usage

### Create rails project

* Install rails bundle into empty folder
```
  mkdir rails_project
  cd rails_project
  docker-bundle install rails
```

*  Init rails project
```
  # create rails project in docker
  docker-bundle rails:new

  # ...
  # configure your database connection (databases.yml)
  # ...

  # init rails database
  docker-bundle rails:seed
```

### Launch exist rails project

* Sync rails depends && databases
```
  cd some_rails_project

  # ...
  # configure your database connection (databases.yml)
  # ...

  docker-bundle rails:seed # for first launch
  # or
  docker-bundle rails:sync # for update database && depends
```

###  Operation

* Run
```
  docker-bundle up
```
* Down
```
  docker-bundle down
```
* Shell
```
  docker-bundle shell
```
or
```
  docker-bundle run bash
```

## In your docker-bundled project:

Other people want launch rails project without install docker-bundle into system

Use

```
  docker/bundle
```
Run docker-bundle directly

Or

```
  docker/bundlew
```
Run docker-bundle in docker environment