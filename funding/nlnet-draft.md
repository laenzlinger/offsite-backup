# NLnet NGI Zero Commons Fund — Application Draft

Deadline: June 1st 2026, 12:00 CEST
Apply at: https://nlnet.nl/propose/
Call: NGI Zero Commons Fund

---

## Proposal name

Open Offsite Backup Appliance

## Website / wiki

https://github.com/laenzlinger/offsite-backup

## Abstract

This project delivers a complete open hardware and open source offsite backup appliance.
The device is a custom carrier board for the Raspberry Pi CM4/CM5 Compute Module with a
PCIe SATA controller (ASM1061), Gigabit Ethernet, and a battery-backed RTC for scheduled
wake/sleep operation. It connects a standard SATA hard disk, receives encrypted backups
over the network, and shuts down until the next scheduled run — consuming near-zero power
between backups.

The goal is a plug-and-forget device that a non-technical person can host: plug in Ethernet,
plug in power, done. All management happens remotely. This enables individuals and small
organizations to maintain sovereign offsite backups on hardware they fully own and control,
without depending on cloud providers.

The entire stack is open:
- Hardware: custom PCB under CERN OHL-P v2, designed in KiCad
- Firmware: none required (ASM1061 uses the standard Linux AHCI driver, no proprietary blobs)
- Software: Raspberry Pi OS + restic + rsync + WireGuard + smartmontools, all open source
- Enclosure: metal case with published design files

I have prior experience designing open hardware for the Raspberry Pi Compute Module through
the Open Pedalboard project (https://github.com/pedalboard/pedalboard-hw), an OSHWA-certified
(CH000023) audio processing platform. That project's CM connector, power supply, and CI
pipeline are directly reused in this design.

## Requested Amount

15000 (in Euro)

## Budget breakdown

| Task | Effort | Cost |
|------|--------|------|
| 1. PCB schematic design (ASM1061, CM connector, PSU, RTC, Ethernet) | 80h | €4,000 |
| 2. PCB layout (4-layer, impedance-controlled PCIe/SATA routing) | 60h | €3,000 |
| 3. Prototype fabrication + assembly (2 board revisions, 5 units each) | — | €2,000 |
| 4. Software stack (OS image, backup automation, monitoring, RTC wake) | 40h | €2,000 |
| 5. Metal enclosure design + prototype | 20h | €1,500 |
| 6. Documentation (build guide, deployment guide, KiBot CI) | 20h | €1,000 |
| 7. Testing + validation (SMART, PCIe throughput, power, thermal) | 20h | €1,000 |
| **Component sourcing (ASM1061, CM connectors, SATA, RTC, passives)** | — | €500 |
| **Total** | **240h** | **€15,000** |

Rate: €50/h for engineering time. Fabrication and components at cost.

## Other funding sources

No other funding. This is a personal project that I am bootstrapping.

## Compare with existing efforts / technical challenges

Existing offsite backup solutions fall into two categories:

1. Cloud backup services (Backblaze, AWS S3, etc.) — proprietary, recurring cost,
   data leaves your control, subject to foreign jurisdiction.

2. Commercial NAS devices (Synology, QNAP) — closed firmware, expensive for a
   single-purpose offsite backup, not designed for unattended remote deployment.

Open hardware CM4/CM5 carrier boards exist (e.g. Uptime Lab Timon, official IO Board),
but none are purpose-built for offsite backup with:
- Native PCIe SATA (no USB bottleneck, no firmware blobs)
- RTC-based scheduled wake for minimal power consumption
- A complete software stack for encrypted backup reception
- An enclosure designed for non-technical deployment

Technical challenges:
- PCIe Gen 2 differential pair routing on a 4-layer PCB (100Ω impedance control)
- SATA signal integrity from ASM1061 to the connector
- Reliable RTC wake via GLOBAL_EN with proper power sequencing
- Creating a reproducible OS image with pre-configured encryption and backup automation

## Ecosystem and engagement

The project targets:
- Privacy-conscious individuals who want offsite backups without cloud dependency
- Small businesses and organizations with GDPR data residency requirements
- The open hardware community (Raspberry Pi, KiCad, OSHWA)
- Self-hosting and homelab communities

Engagement plan:
- All design files published on GitHub under CERN OHL-P v2
- KiBot CI generates interactive BOM, schematics, and 3D views automatically
- OSHWA certification upon completion
- Blog posts / documentation for reproducibility
- Engagement with Raspberry Pi and KiCad communities
- Submission to Crowd Supply or similar for wider distribution if there is demand

---

## Notes for submission

- Call: NGI Zero Commons Fund
- GenAI disclosure: Yes, used for brainstorming project structure and drafting this
  proposal text. All technical decisions and design choices are the applicant's own.
  Prompts and outputs to be attached as required.
