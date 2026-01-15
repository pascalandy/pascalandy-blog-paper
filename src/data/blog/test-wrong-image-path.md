---
title: "Test Post - Wrong Image Path"
pubDatetime: 2026-01-15T10:00:00Z
date_created: 2026-01-15
author: Pascal Andy
description: "Testing if CI catches incorrect image paths"
tags:
  - dev-notes
---

This is a test post with an intentionally wrong image path.

## Wrong path (single ../)

![test-image](../assets/images/og-legacy/2017/11/rsvp-2.jpg)

This should fail because the correct path needs two `../` not one.
