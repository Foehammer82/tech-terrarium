# DataHub

Metadata management tool that is used for tracking metadata of data assets. It is used for discovering, understanding,
and governing data assets.

## Alternatives

### OpenMetadata

I actually set up an instance of OpenMetadata in the Terrarium, but it didn't have as strong of automated lineage as
DataHub and really like DataHub's usage of kafka for streaming metadata. that said, you can spin up a local docker
instance of OpenMetadata in 5-15 minutes by following
their [quick-start](https://docs.open-metadata.org/v1.3.x/quick-start/local-docker-deployment) guide.