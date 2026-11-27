module collector

go 1.27.4

replace golang.org/x/sys => golang.org/x/sys v0.50.0

require (
	github.com/golang-jwt/jwt/v5 v5.3.1
	github.com/sirupsen/logrus v1.10.2
	github.com/stretchr/testify v1.12.1
	gopkg.in/natefinch/lumberjack.v2 v2.2.1
	gopkg.in/yaml.v3 v3.0.1
)

require (
	go.yaml.in/yaml/v3 v3.0.5 // indirect
	golang.org/x/sys v0.50.0 // indirect
)
