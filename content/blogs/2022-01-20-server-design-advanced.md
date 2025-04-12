---
layout: post
title:  "Advanced topics in server design"
date:   2022-01-20
desc: "My views on advanced server design concepts"
keywords: "gh-pages,website,blog,computer science,software engineering,system design,servers, amped"
categories: [Computer Science, System Design, Servers, Backend, Networks, Software Engineering]
tags: [Computer Science, System Design, Servers, Backend, Networks, Software Engineering]
icon: icon-html
---
Reference papers:

\[1\]  [A Scalable and Explicit Event Delivery Mechanism for UNIX](https://www.usenix.org/legacy/publications/library/proceedings/usenix99/full_papers/banga/banga.pdf)

\[2\]  [accept()able Strategies for Improving Web Server Performance](https://www.usenix.org/legacy/event/usenix04/tech/general/full_papers/brecht/brecht.pdf)

## Summary 
Server performance depends on a number of factors and in order to design high performance and scalable servers, it is important to carefully reason about these factors. Authors of [1] and [2] argue that a server’s policies for accepting new client connections [2] and the OS event-notification mechanism [1], have a signif- icant effect on a server’s performance. The authors in [1] highlight that web servers using the OS system call select (or poll) to check for events, scale poorly with the event rate. To mitigate the scalability issue they propose an event-based notification mechanism wherein the kernel maintains a queue of events and notifies the application once an event is ready. This leads to better scalability as the kernel performs work proportional to the number of events. The authors in [2] study another important aspect of server design – the policy for accepting new connections. Through their experiments, they argue that finding the correct balance between accepting new connections and processing existing connections can improve the performance of web servers. They conduct experiments on three different servers and vary the number of consecutively accepted connections using an accept-limit parameter – the results show that well-tuned accept policies yield reasonable improvements as compared to the baseline policy.

## Positive Points
* The authors in [1] explained the API design and implementation very clearly by providing sufficient illustrations and code-examples. The effort they put into profiling the kernel in order to compare the CPU utilization of their API and select provided great insights into the inefficiency of select.
* The authors in [1] provided a survey of event-management APIs in Operating Systems other than UNIX and highlighted how the same ideas were already being successfully used in other Operating Systems like Windows NT.
* The authors in [2] spent great effort in fairly comparing the TUX and μserver by configuring them to function under similar resource limits. This is an important point to consider while comparing different servers.
* The authors in [2] devised an elaborate testing strategy and spent effort in highlighting the drawbacks of a commonly used testing workload. Moreover, they studied the server’s performances under a unique one-packet workload that provided deeper insights.

## Drawbacks
* The authors in [1] claim that the poll system call shares the same scaling problem as select, however they only provide experimental results by comparing their API with select. An experiment showcasing poll performance as well, could back their claim.
* In [1], the authors could have also studied the relationship between the array max parameter and response time to determine whether the increased costs due to increase in array max has any effect on the response time.
* The authors in [2] reported the most interesting accept strategies in the experiments, however they did not elaborate on what alternative strategies they tried and why they chose a particular strategy among others.

## Research Questions
1. Fine-tuning the optimal accept-rate for each server is a time consuming task. As showed in [2], better performance can be observed by dynamically adjusting the accept strategy – Can a “calibration” phase at the starting of a server be used to set an initial accept-limit, and then the load can be monitored in real-time to vary the accept-limit dynamically?
2. In [1], a fixed length queue is maintained per-thread for events pertaining to each file-descriptor. This queue can be replaced with a circular queue which could improve space complexity by making efficient use of free memory.
3. Will the event-notification API proposed in [1] provide similar improvements in a multi-processor environment as it does in a single processor setting? Would there be significant changes in the API implementation to support multi-processor events?