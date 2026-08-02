# No Quiet Fix: Kerckhoffs' Lemma and the July 2026 Seed-Entropy Incident

*Yuri da Silva Villas Boas — author of [BIP-450 (Formosa)](https://github.com/bitcoin/bips/blob/master/bip-0450.mediawiki), creator of the Great Wall protocol. August 2026.*

*Companion post to the [BTC-D20 tutorial](https://github.com/Yuri-SVB/BTC-D20) — a printable kit for generating BIP-39 seeds with a 20-sided die, in four languages.*

**TL;DR** — (1) The infamous "provisional PRNG" code was not consciously waved through: a build-system guard checked whether a macro was *defined* rather than whether it was *true*, so code that was never meant to ship ran in production for five years, invisibly. (2) The wish that users could have been warned "discreetly" runs into what I'll call **Kerckhoffs' Lemma**: any channel wide enough to reach the victims is wide enough to reach the attacker. There is no such thing as a quiet fix for a fleet-wide secret. (3) Its **corollary**: the absence of attacks before day zero is not obscurity working — the catastrophe was contracted the moment the bug shipped, and every quiet month only grew the blast radius. (4) Consequences: the failure class is *amplified* by hardware wallets, *preemptively solved* by physically verified entropy, and *mitigable* by memory-hard key derivation — and the same corollary indicts the custody layer's collective hush: staying quiet about designs that leave a feasible-but-slower path to the funds protects no one, because wrench attackers work that out on their own (the attack registry shows they already have) while holders stay uninformed. The answer is custody that survives full disclosure.

## 1. The comment everyone is quoting

Since the July 30 sweeps, screenshots of the 2021 firmware code have circulated widely, with an inline comment acknowledging the software PRNG path as less than ideal — provisional code, marked as such. The recurring reaction has been perplexity: *how could developers see that comment and ship it anyway?*

The technical post-mortems ([Block Engineering's analysis](https://engineering.block.xyz/blog/predictable-rng-fallback-and-32-bit-reseed-in-coldcard-firmware), [Coinkite's own backgrounder](https://blog.coinkite.com/entropy-technical-backgrounder/)) support a more precise — and more unsettling — answer: **nobody decided to ship it.** When wallet generation migrated to the `libngu` library in March 2021, an `#ifndef` guard checked whether the macro `MICROPY_HW_ENABLE_RNG` was *defined*, not whether its value was nonzero. It was defined — as zero. The result: the fallback path (a Yasmarang software PRNG seeded from the chip's serial number and timer registers — public, reconstructible data) silently became the production path, while everyone believed the hardware RNG was in use. Effective entropy on Mk3 devices: roughly 40 bits, instead of the 128 a 12-word seed promises.

The comment did its job: it marked intent. The build system betrayed the intent, and **no one could see which path was actually live** — not the developers, not auditors reading the source with the same mental preprocessor, and least of all users. The perplexity aimed at the comment is really perplexity about unverifiable state. Hold that thought.

## 2. "Why not warn users quietly?" — Kerckhoffs' Lemma

The second recurring reaction: *couldn't this have been disclosed to users discreetly, so honest people could migrate before attackers learned of it?*

No — and it is worth being precise about why, because the impossibility is structural, not a failure of cleverness. Call it **Kerckhoffs' Lemma**: **knowledge injected into a large, anonymous population diffuses; you cannot direct information at "users only," because attackers are embedded in every channel users occupy.** *Lemma*, not corollary — this is the premise Kerckhoffs' principle rests on, not a consequence of it: his 1883 second desideratum justifies "assume the enemy knows the system" precisely by the assumption that the system "may fall into the hands of the enemy without inconvenience." First the impossibility of containment; then "don't rely on obscurity" as its conclusion. The 2026 twist is merely speed: diffusion that took campaigns in Kerckhoffs' day now takes hours. Concretely:

- A firmware patch is a public diff. Diffing a release against its predecessor reconstructs the vulnerability — this is standard attacker practice, automated, within hours.
- A mass notification (email, in-app banner, vendor blog) is public the moment it reaches thousands of inboxes; one screenshot suffices.
- Even silent migration is broadcast: a wave of same-pattern fund movements from a vendor's known UTXO fingerprints is itself an on-chain announcement of *"something is wrong; here is who has not moved yet."*

So "warn the good guys first" was never an option that responsible people declined. It is an option that does not exist. The only disclosures that work are the ones designed for a world where **disclosure and attack start the same clock** — which is exactly what we watched: sweeps under way while most users were still asleep.

**And a corollary follows** — this one genuinely *derived* from the lemma: **the absence of attacks before day zero is not evidence that obscurity is working.** The five quiet years between March 2021 and July 2026 were not safety; they were accumulation. The catastrophe was already contracted the moment the flawed firmware shipped — every additional quiet month only enrolled more wallets into the eventual sweep. "Nobody has exploited it yet, so let's all be quiet about it" does not avoid the reckoning; it compounds it. On the lemma's clock, the choice is never between attack and no attack — only between a smaller, earlier day zero and a bigger, later one. That is why responsible disclosure carries deadlines, and why silence is not a neutral act.

Designs are safe when they survive *full* publication of their mechanism. Which brings us to what that implies.

## 3. Takeaways

### 3.1 Hardware wallets amplify this failure class

This is not an argument against hardware wallets — signing on a dedicated, air-gapped device remains best practice. But at *seed-generation* time their economics invert: one firmware image generates seeds for an entire fleet, so a single invisible bug becomes a perfectly correlated, fleet-wide failure with a five-year fuse. The device's trust halo suppresses the suspicion that would meet a random web tool, and air-gapping does nothing when the flaw ships inside the box. Monoculture plus opacity is the amplifier.

### 3.2 The preemptive fix exists, is physical, and just passed an empirical test

Entropy you *watched happen* is the one entropy no vendor, auditor or preprocessor can silently take from you. The vendor's own advisory notes that seeds generated from 50+ fair dice rolls were never at risk — dice users sailed through this incident untouched. That is the entire thesis of the [BTC-D20 kit](https://github.com/Yuri-SVB/BTC-D20): a printable lookup table and a D20 give you all 128 (or 256) bits from rolls you verify with your own eyes, with the worked examples machine-checked against the official wordlist, which the build pulls directly from `bitcoin/bips` at a pinned commit.

### 3.3 Memory-hard KDFs would have changed the economics

BIP-39 stretches the mnemonic with PBKDF2-HMAC-SHA512 at 2048 iterations — deliberately light, fine when the input has full entropy, and nearly free for an attacker when it does not. A **memory-hard KDF** (scrypt, Argon2id) between entropy and keys raises the *per-guess* cost by orders of magnitude in both time and silicon. It cannot turn 40 bits into 128 — weak entropy stays weak — but it converts "sweep a fleet in 41 minutes" into a capital-intensive campaign that buys victims days or weeks on the very clock that Kerckhoffs' Lemma says starts at disclosure. Mitigation, not absolution: you still want the dice. This layering — verifiable entropy at generation (this kit), the mnemonic encoding itself (Formosa, BIP-450: a forwards- and backwards-compatible expansion of BIP-39 — an encoding, not a KDF), and memory-hard derivation with coercion-resistant custody (Great Wall) — is the program of the [Great Wall](https://github.com/Yuri-SVB) line of work.

### 3.4 The corollary stalks the $5-wrench problem too

This last one is more tentative, and it is the strategic heart of the matter. Bitcoin's prevailing answer to physical coercion is obscurity, at two levels. At the individual level: keep a low profile, deny holdings if asked, deny harder under attack. That level is not the target here — low profile is good hygiene, and for a lone holder with nothing better to migrate to, denial is individually rational. The analogy bites at the **collective** level: the tacit norm that says *don't tell around that protocols leaving a feasible-but-slower path to the funds are dangerous* — it would scare people, or worse, instruct attackers.

That norm is the pre-day-zero hush replayed at the scale of a design class, and both halves of it fail the same way the firmware silence did. It does not inform attackers: **wrench attackers derive the flaw operationally** — escalation and persistence are their proof of concept, and the [public registry of physical bitcoin attacks](https://github.com/jlopp/physical-bitcoin-attacks) shows the numbers of a discovery already made. And it does not protect holders: it only keeps them adopting gray-area designs believed safe, while the corollary runs — **the quiet years are not the designs working; they are the exposed install base compounding.** Absence of a wave of attacks against a given custody scheme is no more evidence of its coercion-resistance than five quiet years were evidence of a healthy RNG.

Saying this out loud feels, short term, like an aggravation — the same way publishing a proof of concept feels like arming attackers. But disclosure of a *design class* exposes no individual, and Kerckhoffs' conclusion transfers whole: the only custody worth having is custody that remains safe when the attacker knows *everything* — that you hold coins, roughly how much, and exactly which protocol guards them. Coercion-resistance under full disclosure, not collective hush, is the custody-layer analogue of "assume the enemy knows the system." Making that bar explicit — and classifying which designs meet it by which route — is the program of the Great Wall protocol and its accompanying threat-model work.

## Sources

- [Block Engineering — Predictable RNG Fallback and 32-Bit Reseed in COLDCARD Firmware](https://engineering.block.xyz/blog/predictable-rng-fallback-and-32-bit-reseed-in-coldcard-firmware)
- [Coinkite — Technical Deep Dive into the Entropy Issue](https://blog.coinkite.com/entropy-technical-backgrounder/)
- [CoinDesk — Major bitcoin wallet flaw drains 594 BTC in 25-minute sweep](https://www.coindesk.com/tech/2026/07/31/major-bitcoin-wallet-flaw-drains-594-btc-in-25-minute-sweep)
- [The Hacker News — Coldcard Hardware Wallet Flaw Linked to $70 Million Bitcoin Theft in 41 Minutes](https://thehackernews.com/2026/08/coldcard-hardware-wallet-flaw-linked-to.html)
- [CryptoTimes — Coldcard Hack Tops $88.6M as Galaxy Finds Third Attack Wave](https://www.cryptotimes.io/2026/08/02/coldcard-hack-tops-88-6m-as-galaxy-finds-third-attack-wave/)

*Figures and attribution are as reported at the time of writing and may still evolve; nothing here is financial advice. Tone note: the vendor patched within a day and published a candid post-mortem — the argument above is about a failure class, not a company.*
