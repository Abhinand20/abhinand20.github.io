---
layout: post
title:  "Flash: An efficient and portable Web Server"
date:   2022-01-16
desc: "My views on the Flash web server"
keywords: "gh-pages,website,blog,computer science,software engineering,servers,server design"
categories: [Computer Science, System Design, Servers, Backend, Software Engineering]
tags: [Computer Science, System Design, Servers, Backend, Software Engineering]
icon: icon-html
---
The reference paper can be found [here.](https://www.usenix.org/legacy/events/usenix99/full_papers/pai/pai.pdf)
## Summary 
In this paper, the authors propose Flash – an efficient and portable web server that utilizes an asymmetric multi-process even-driven (AMPED) architecture. This architecture is a combination of the single-process event-driven (SPED) and multi-process/multi-thread (MP/MT) architectures. Flash consists of a main process that handles HTTP requests in an event-driven fashion, and it uses several asynchronous helper processes to perform blocking operations on the disk. The authors provide a brief overview of the different types of server architectures and analyze their server’s performance compared to Zeus (SPED) and Apache (MP/MT) servers as benchmarks. The authors also introduce several important optimizations in caching, byte alignment, file access via mmap and checking for memory residency before calling helper processes which result in large performance gains. Most of these optimizations are fairly standard in present-day web servers but at the time the paper was published, these ideas were quite novel.

## Positive Points
* The paper provides great insights about key points to consider while designing web servers. It also provides a detailed comparison based on performance characteristics of each design choice.
* The evaluation experiments are conducted in an exhaustive manner with carefully drawn out workloads that tested the server’s performance at its maximum capacity. The evaluation workflow is exemplary.
* The paper introduces many optimization ideas that are widely used and applicable in present-day web servers. The ideas of application-level caching with both data and computation caches, DMA for scatter-gather support etc. are ideas that were quite novel at the time the paper was published.

## Drawbacks
* At the time this paper was published, most web servers mainly handled static data. However, in present day servers the content is increasingly dynamic. Therefore the claim that most non-blocking IO operations are just disk reads is not true anymore.
* The paper does not talk about sendfile() which is a non-blocking system call that uses Direct Memory Access (DMA) to copy a file’s contents into OS memory directly.
* The authors ran most of the evaluation experiments on in a LAN setting and their WAN evaluations were also simulated on LAN. Nowadays, most of the clients interact with servers through WAN.

## Research Questions
1. Present day web-servers serve increasingly dynamic content – how would a server like Flash handle such work loads? Creating a new process for each dynamic request may not be feasible.
2. Why did Flash lose against competitors like Apache, which also have adopted many ideas from Flash?
3. Can sendfile() (and related syscalls) be used to handle blocking disk operations instead of multiple threads/processes? Are there any caveats?