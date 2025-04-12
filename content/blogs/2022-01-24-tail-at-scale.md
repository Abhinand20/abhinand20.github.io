---
layout: post
title:  "Distributed systems: Stragglers"
date:   2022-01-24
desc: "My views on the tail at scale problem"
keywords: "gh-pages,website,blog,computer science,software engineering,system design,distributed systems, latency"
categories: [Computer Science, System Design, Distributed Systems, Backend, Networks, Software Engineering]
tags: [Computer Science, System Design, Distributed Systems, Backend, Networks, Software Engineering]
icon: icon-html
---
Reference paper:

- [The Tail at Scale](https://dl.acm.org/doi/abs/10.1145/2408776.2408794?download=true)

## Summary 
One of the challenges in building large-scale systems is to consistently maintain low-latency in responses. Dean and Barroso, in their paper highlight techniques that can be used to build distributed systems that have an overall low-latency despite its constituent components having occasional high-latency.
The authors first provide several reasons that contribute to high tail latency such as shared resources, queuing, daemons, garbage collection etc. and then they show that variability in latency of individual components lead to high overall service latency due to the “fan-out” architecture generally adopted in large-scale systems. The authors take inspiration from fault-tolerant systems and focus on techniques that reduce latency hiccups regardless of root cause. Finally, the authors introduce techniques such as sending the same request to multiple replicas and only considering the first response (hedged requests) and allowing multiple servers to communicate updates regarding requests (tied requests) to reduce tail latency. Other techniques proposed by the authors such as micro-partitioning, selective replication and latency-induced probation also lead to significant reduction in latency at larger scales.

## Positive Points
* The authors made the paper accessible to a wider audience by using sufficient examples and metrics from real-world services provided by google. For example, the graph showing how the probability of high-service latency scales with number of servers was very insightful.
* In the last few sections of the paper, the authors provide important considerations to keep in mind while building production quality robust distributed systems such as canary requests. These techniques are also applicable to a broader range of services apart from information retrieval.
* For several design techniques that the authors proposed, they highlighted various trade-offs that were made in adopting those techniques. For example, the good-enough results provided by google search and skipping non-essential subsystems. Such accounts provide a deeper understanding of the issues faced in large-scale systems.


## Drawbacks
* For some proposed techniques such as latency-induced probation and selective replication the authors do not carry out evaluations. It would have been helpful if they included some statistics about these techniques.
* The authors do not discuss the implications that write operations would have on their proposed techniques. For example, if we issue two write operations in hedged requests, a change may be made twice.
* The authors could have provided experiments that compare directly reducing component-level variability vs tail-tolerant techniques that mask or work around temporary latency pathologies to further enforce their points.


## Research Questions
1. How would latency-induced probation work in case of writing to a server on probation?
2. In a complex large-scale distributed system, there are a lot of moving parts. How can one identify issues that
are specially caused by latency variability? For example, some latency issues could be caused by faults/retries.
3. One of the modern commercial databases that use hedged requests is Cassandra. It uses the percentile heuristic to send 3 requests for each request. This increases the load on the server but provides better latency.