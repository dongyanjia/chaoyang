# Doris 4.0 镜像选项

如果 `selectdb/doris-fe-ubuntu:4.0.0` 镜像无法拉取，可以尝试以下替代方案：

## 方案 1: SelectDB 官方镜像（推荐）
```yaml
image: selectdb/doris-fe-ubuntu:4.0.0
image: selectdb/doris-be-ubuntu:4.0.0
```

## 方案 2: Apache 官方镜像（如果可用）
```yaml
image: apache/doris:fe-2.1.0
image: apache/doris:be-2.1.0
```

## 方案 3: 使用最新稳定版本
```yaml
image: apache/doris:fe-latest
image: apache/doris:be-latest
```

## 方案 4: 手动构建（如果官方镜像不可用）

如果以上镜像都不可用，可以：

1. 查看可用镜像：
```bash
docker search doris
```

2. 或者从源码构建：
```bash
git clone https://github.com/apache/doris.git
cd doris
docker build -t doris-fe:4.0.0 -f docker/thirdparties/docker/fe/Dockerfile .
docker build -t doris-be:4.0.0 -f docker/thirdparties/docker/be/Dockerfile .
```

## 检查可用镜像

运行以下命令查看可用的镜像：

```bash
# 查看 SelectDB 镜像
docker search selectdb/doris

# 查看 Apache 镜像
docker search apache/doris
```

## 当前配置

当前 `docker-compose.yml` 使用：
- FE: `selectdb/doris-fe-ubuntu:4.0.0`
- BE: `selectdb/doris-be-ubuntu:4.0.0`

如果这些镜像不可用，请告诉我，我会帮您调整配置。
