django-nginx-pubsub
===================

A rough (incomplete) implementation of catching django signals and pushing that information to an nginx pubsub channel. Started work on handling issues of sharding multiple pubsub servers and creating rooms for each individual user, though this code needs to be revisited before being used anywhere.
