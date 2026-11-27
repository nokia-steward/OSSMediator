module elasticsearchplugin

go 1.27.4

replace golang.org/x/sys => golang.org/x/sys v0.50.0

require (
	github.com/fsnotify/fsnotify v1.10.1
	github.com/sirupsen/logrus v1.10.2
	gopkg.in/natefinch/lumberjack.v2 v2.2.1
)

require golang.org/x/sys v0.50.0 // indirect
