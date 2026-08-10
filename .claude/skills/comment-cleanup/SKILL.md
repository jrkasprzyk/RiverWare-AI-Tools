---
name: comment-cleanup
description: Clean up the comments in AI-written code, so that the file describes what the code is and not how the assistant built it. Delete change-history comments ("added", "now handles", "in this version"). Delete comments that repeat the code. Give each tuning parameter a comment with its range, default, units, and effect. Write every comment in Simplified Technical English. Use this skill when the user asks to clean up comments, remove AI slop comments, fix comment noise, document tuning parameters or magic numbers, or make an AI-written file readable. Also apply these rules when you write or edit any comment in this repository, even if the user does not mention comments.
---

# Comment cleanup (bridge)

This is a thin bridge for users who cloned this repository directly.
The full skill is at `skills/comment-cleanup/SKILL.md`. Read that file and
follow it.
