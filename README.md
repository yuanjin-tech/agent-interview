# AI Interview

一个面向 **Agent 应用开发岗位求职者** 的中文开源面试题库。

本项目通过社区协作持续收集、修订和完善 Agent 应用开发相关的面试题与参考答案，帮助求职者系统理解核心概念、工程方法和真实项目中的常见问题，同时也为面试官提供可复用的题目参考。

## 内容校验

校验目录元数据、UUID、题目文件、正文标题和本地链接是否一致：

```bash
uv sync
make validate
```

运行全部单元测试：

```bash
make test
```

## 本地预览网站

网站使用 Astro 将 `catalog.yaml` 和 `questions/*.md` 构建为纯静态页面。请使用 Node.js 22.19 或更高版本：

```bash
make site-install
make site-dev
```

生成可部署文件：

```bash
make site-build
```

构建结果位于 `site/dist/`。推送到 `main` 分支后，`.github/workflows/deploy-pages.yml` 会先校验题库、运行测试，然后构建并发布到 GitHub Pages。首次发布前，需要在仓库的 **Settings → Pages → Build and deployment** 中将 Source 设为 **GitHub Actions**。

## 开源许可

- 题库内容与文档采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh-hans) 许可，允许分享、改编和商业使用，但须署名并说明是否作出修改。
- 辅助脚本与工程文件采用 [MIT License](LICENSE-CODE) 许可。

具体适用范围见 [LICENSE](LICENSE)。
