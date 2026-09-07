# Git Hook Inputs

| Hook | Arguments | Standard input | Can block? |
|---|---|---|---|
| `pre-commit` | none | none | yes |
| `commit-msg` | message file | none | yes |
| `pre-rebase` | upstream, optional branch | none | yes |
| `pre-push` | remote name, URL | local and remote ref records | yes |
| `pre-receive` | none | old SHA, new SHA, ref records | yes |
| `update` | ref, old SHA, new SHA | none | yes |
| `post-receive` | none | old SHA, new SHA, ref records | no |

Read all standard-input records. Handle the all-zero SHA for ref creation or deletion. Quote arguments and parse records without whitespace splitting.

`pre-commit` usually validates the index. `commit-msg` validates the supplied message file. `pre-push` must examine the exact records supplied by Git, including new branches and deletions. Post hooks report or trigger asynchronous work but cannot reject the completed operation.

Bypass flags affect only specific client hooks. They do not bypass every hook or server policy. Agents must not use bypasses without explicit user authorization.
