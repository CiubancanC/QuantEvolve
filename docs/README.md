# QuantEvolve Documentation

## 📚 Table of Contents

### Core Documentation

- **[QuantEvolve Research Paper](QuantEvolve.md)** - Full research paper describing the methodology
- **[Implementation Deviations](DEVIATIONS.md)** - Differences from the paper and rationale
- **[Improvements Log](IMPROVEMENTS.md)** - Enhancement history and lessons learned

### Paper Trading

- **[Quick Start Guide](paper_trading/START_HERE.md)** - Get started in 5 minutes
- **[Complete Trading Guide](paper_trading/AUTOMATED_TRADING_GUIDE.md)** - Full documentation, troubleshooting, advanced options
- **[Trading Summary](paper_trading/PAPER_TRADING_SUMMARY.md)** - Quick reference card

### Blog & Publications

- **[Blog Post Draft](blog_post.md)** - Write-up of evolution results and methodology

---

## 🚀 Quick Navigation

### Getting Started
1. Read the [main README](../README.md) for installation and basic usage
2. For paper trading, start with [START_HERE.md](paper_trading/START_HERE.md)
3. For deep dives, see the [Research Paper](QuantEvolve.md)

### Developer Resources
- [CLAUDE.md](../CLAUDE.md) - Developer guide for working with the codebase
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines

---

## 📖 Document Descriptions

### Core Documentation

#### [QuantEvolve.md](QuantEvolve.md)
The complete research paper implementation. Covers:
- Evolutionary algorithm design
- Multi-agent LLM system
- Feature map architecture
- Quality-diversity optimization
- Experimental results

#### [DEVIATIONS.md](DEVIATIONS.md)
Documents implementation choices that differ from the paper:
- Backtesting framework (custom vs Zipline)
- LLM inference (OpenRouter vs local)
- Data handling and assumptions
- Rationale for each deviation

#### [IMPROVEMENTS.md](IMPROVEMENTS.md)
Chronological log of enhancements:
- Bug fixes and optimizations
- Feature additions
- Lessons learned
- Performance improvements

### Paper Trading Documentation

#### [START_HERE.md](paper_trading/START_HERE.md)
**Your first stop for paper trading**. Quick start guide covering:
- 3-command setup
- What happens automatically
- Monitoring schedule
- Important notes

#### [AUTOMATED_TRADING_GUIDE.md](paper_trading/AUTOMATED_TRADING_GUIDE.md)
**Comprehensive reference**. Includes:
- Detailed daemon operation
- All control commands
- Troubleshooting guide
- Advanced configuration
- Data management
- After 30-days analysis

#### [PAPER_TRADING_SUMMARY.md](paper_trading/PAPER_TRADING_SUMMARY.md)
**Quick reference**. At-a-glance:
- Component overview
- Quick start commands
- File locations
- Verification checklist

### Blog & Publications

#### [blog_post.md](blog_post.md)
Comprehensive write-up of the QuantEvolve project:
- Results and performance
- Methodology overview
- Lessons learned
- Next steps (paper trading validation)
- Ready for publication

---

## 🔍 Finding What You Need

| I want to... | Read this... |
|--------------|--------------|
| Understand the research | [QuantEvolve.md](QuantEvolve.md) |
| Set up paper trading quickly | [START_HERE.md](paper_trading/START_HERE.md) |
| Troubleshoot paper trading | [AUTOMATED_TRADING_GUIDE.md](paper_trading/AUTOMATED_TRADING_GUIDE.md) |
| Understand implementation choices | [DEVIATIONS.md](DEVIATIONS.md) |
| See what's changed recently | [IMPROVEMENTS.md](IMPROVEMENTS.md) |
| Contribute to the project | [CONTRIBUTING.md](../CONTRIBUTING.md) |
| Work with the code | [CLAUDE.md](../CLAUDE.md) |
| Share the project | [blog_post.md](blog_post.md) |

---

## 📁 Documentation Structure

```
docs/
├── README.md (this file)           # Documentation index
├── QuantEvolve.md                   # Research paper
├── DEVIATIONS.md                    # Implementation notes
├── IMPROVEMENTS.md                  # Change log
├── blog_post.md                     # Blog post draft
└── paper_trading/                   # Paper trading docs
    ├── START_HERE.md                # Quick start
    ├── AUTOMATED_TRADING_GUIDE.md   # Complete guide
    └── PAPER_TRADING_SUMMARY.md     # Summary
```

---

**Need help?** Check the [main README](../README.md) or [file an issue](https://github.com/CiubancanC/QuantEvolve/issues).
