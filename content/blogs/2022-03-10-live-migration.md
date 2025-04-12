---
layout: post
title:  "Live VM Migration"
date:   2022-03-10
desc: "My views on live VM migration techniques"
keywords: "gh-pages,website,blog,computer science,software engineering,system design,distributed systems, file systems"
categories: [Computer Science, System Design, Distributed Systems, Backend, File systems, Software Engineering, Storage]
tags: [Computer Science, System Design, Distributed Systems, Backend, File systems, Software Engineering, Storage]
icon: icon-html
---
Reference papers:

\[1\] [Live Migration of Virtual Machines](https://www.usenix.org/legacy/events/nsdi05/tech/full_papers/clark/clark.pdf)

## Summary 
Clark et al. propose an approach to migrating live VMs across different instances with minimal degradation of the quality of service and downtime. Live migration is particularly helpful for load re-balancing, fault management and server maintenance. The authors first describe the traditional approaches to live migration including stop-and-copy, demand- copy, pre-copy and other hybrid methods. The authors adopt pre-copy as their approach because of its efficiency. The authors describe the various design considerations in their approach and provide solutions to migrating storage (NAS) and network connections between instances with minimal downtime. The main idea of their approach is to iteratively pre-copy the VM’s page tables onto another VM without stopping it. Once majority of the pages have been migrated, the VM is brought to a complete stop and the final transfer of state is initiated. This approach of iterative copying results in very minimal downtime during migration. Finally, the authors extensively study the performance of their live migration approach on various benchmarks involving static load web-servers, dynamic content generating servers and also interactive gaming servers. Some optimizations discussed by the authors for their approach include adaptive rate-limiting, freeing page cache pages and other paravirtualization optimization. The evaluation results on several benchmarks showed the applicability of the author’s live migration approach.

## Positive Points
* The idea of dynamic rate-limiting is quite interesting as it adapts the migration process according to the load on the VM hence allowing the migration process to have minimal impact on the quality of service of the VM.
* The analysis on writable working sets (WWS) is very well carried out and it is quite interesting. Since their approach relies on copying VM page table entries, it is pertinent to evaluate how frequently these entries get invalidated and develop a solution based on this heuristic.
* The paper provides a thorough and comprehensive overview of the topic of live migration of virtual machines, covering various aspects such as benefits, challenges, techniques, and impact on system performance. It provides a holistic understanding of the subject matter without assuming the reader to have extensive knowledge in the domain.

## Drawbacks
* The authors do not conduct a comparative evaluation study between their proposed migration approach and other existing methods mentioned in the paper such as Denali and Zap. It would have been interesting for the readers to understand how the author’s approach compares to other approaches in terms of performance and downtime.
* The authors only consider migration of VMs in a setting that does not utilize local disks and rather uses NAS, and they do not implement migration over the WAN. Presently, many clusters utilize SSDs as a means of storage rathe than NAS, and are spread across the globe geographically. It would have been good if the authors provided concrete solution for adopting their approach in such settings. The authors however present some high-level ideas to deal with local storage migration such as software RAIDs.
* The paper lacks a discussion on fault-tolerance in cases where migration fails to complete. For instance, it is possible that during the stop-and-copy phase, the destination machine crashes, then there should be mechanisms in place to detect failure and rollback the migration.

## Research Questions
1. What fault-tolerance and recovery mechanisms can be adopted during live migration?
2. Can we utilize live migration to dynamically load-balance applications? – maybe a controller can monitor the state of the cluster and migrate heavily loaded VMs to other machines where load is less.
3. How can this approach of live migration be adopted to migrate instances over the WAN?