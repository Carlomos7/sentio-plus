"use client";

import { motion } from "framer-motion";
import Image from "next/image";
import {
  MessageSquare,
  Database,
  TrendingUp,
  Search,
  BarChart3,
  ArrowRight,
  Check,
  Zap,
  Shield,
  Clock,
  Play,
} from "lucide-react";

const fadeInUp = {
  initial: { opacity: 0, y: 30 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.6 },
};

const staggerContainer = {
  animate: {
    transition: {
      staggerChildren: 0.1,
    },
  },
};

export default function Home() {
  return (
    <div className="min-h-screen bg-white">
      <Navbar />
      <Hero />
      <TrustedBy />
      <Features />
      <HowItWorks />
      <ChatPreview />
      <Pricing />
      <CTA />
      <Footer />
    </div>
  );
}

function Navbar() {
  return (
    <motion.nav
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="fixed top-0 left-0 right-0 z-50 backdrop-blur-xl bg-white/80 border-b border-sentio-border"
    >
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Image
            src="/sentio-logo.png"
            alt="Sentio"
            width={120}
            height={32}
            className="h-8 w-auto"
          />
        </div>
        <div className="hidden md:flex items-center gap-8">
          <a href="#features" className="text-sentio-gray hover:text-sentio-dark transition-colors">
            Features
          </a>
          <a href="#how-it-works" className="text-sentio-gray hover:text-sentio-dark transition-colors">
            How it Works
          </a>
          <a href="#pricing" className="text-sentio-gray hover:text-sentio-dark transition-colors">
            Pricing
          </a>
        </div>
        <div className="flex items-center gap-4">
          <button className="hidden sm:block text-sentio-gray hover:text-sentio-dark transition-colors font-medium">
            Sign In
          </button>
          <button className="px-5 py-2.5 rounded-full btn-primary text-white font-medium">
            Try Demo
          </button>
        </div>
      </div>
    </motion.nav>
  );
}

function Hero() {
  return (
    <section className="pt-32 pb-20 px-6 hero-bg grid-pattern">
      <div className="max-w-7xl mx-auto">
        <motion.div
          variants={staggerContainer}
          initial="initial"
          animate="animate"
          className="text-center max-w-4xl mx-auto"
        >
          <motion.div
            variants={fadeInUp}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-sentio-blue/5 border border-sentio-blue/20 mb-8"
          >
            <span className="w-2 h-2 rounded-full bg-sentio-blue animate-pulse" />
            <span className="text-sm text-sentio-blue font-medium">Powered by Vector Intelligence</span>
          </motion.div>

          <motion.h1
            variants={fadeInUp}
            className="text-5xl md:text-7xl font-bold leading-tight mb-6 text-sentio-dark"
          >
            Stop Reading Reviews.
            <br />
            <span className="text-gradient">Start Understanding Them.</span>
          </motion.h1>

          <motion.p
            variants={fadeInUp}
            className="text-xl text-sentio-gray max-w-2xl mx-auto mb-10"
          >
            Transform thousands of customer reviews into instant insights. Our AI captures
            the semantic meaning of every review, so you can chat naturally and discover
            what your customers really think.
          </motion.p>

          <motion.div
            variants={fadeInUp}
            className="flex flex-col sm:flex-row items-center justify-center gap-4"
          >
            <button className="group px-8 py-4 rounded-full btn-primary text-white font-semibold text-lg flex items-center gap-2">
              Try Interactive Demo
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </button>
            <button className="px-8 py-4 rounded-full border border-sentio-border text-sentio-dark font-medium hover:bg-sentio-light transition-colors flex items-center gap-2">
              <Play className="w-5 h-5" />
              Watch 2-Min Video
            </button>
          </motion.div>

          <motion.p variants={fadeInUp} className="text-sm text-sentio-gray mt-6">
            No credit card required • Free 14-day trial
          </motion.p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="mt-20 relative"
        >
          <div className="rounded-2xl border border-sentio-border card-shadow bg-white p-2">
            <div className="bg-sentio-light rounded-xl p-6 md:p-8">
              <div className="flex items-center gap-2 mb-6">
                <div className="w-3 h-3 rounded-full bg-red-400" />
                <div className="w-3 h-3 rounded-full bg-yellow-400" />
                <div className="w-3 h-3 rounded-full bg-green-400" />
                <span className="ml-4 text-sm text-sentio-gray">sentio-chat.app</span>
              </div>
              <DashboardPreview />
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

function DashboardPreview() {
  return (
    <div className="grid md:grid-cols-2 gap-6">
      <div className="space-y-4">
        <div className="bg-white rounded-xl p-5 border border-sentio-border card-shadow">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-sentio-blue to-sentio-blue-light flex items-center justify-center">
              <MessageSquare className="w-5 h-5 text-white" />
            </div>
            <div>
              <p className="font-semibold text-sentio-dark">Sentio AI</p>
              <p className="text-xs text-sentio-gray">Analyzing 12,847 reviews...</p>
            </div>
          </div>
          <div className="space-y-3">
            <div className="bg-sentio-light rounded-lg p-3 text-sm">
              <p className="text-sentio-gray mb-1 text-xs font-medium">You asked:</p>
              <p className="text-sentio-dark">&quot;What are the main complaints about our mobile app?&quot;</p>
            </div>
            <div className="bg-sentio-blue/5 rounded-lg p-3 text-sm border border-sentio-blue/20">
              <p className="text-sentio-blue mb-2 text-xs font-medium">Analysis complete:</p>
              <p className="text-sentio-dark">
                Based on 2,341 reviews mentioning the mobile app, the top 3 concerns are:
              </p>
              <ul className="mt-2 space-y-1 text-sentio-gray text-sm">
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-red-400" /> Slow loading times (38%)
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-yellow-400" /> Checkout bugs (27%)
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-orange-400" /> Push notification issues (19%)
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
      <div className="space-y-4">
        <div className="bg-white rounded-xl p-5 border border-sentio-border card-shadow">
          <p className="text-sm font-semibold text-sentio-dark mb-4">Sentiment Overview</p>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-sentio-gray">Positive</span>
                <span className="text-green-600 font-medium">67%</span>
              </div>
              <div className="h-2 bg-sentio-light rounded-full overflow-hidden">
                <div className="h-full w-[67%] bg-gradient-to-r from-green-500 to-emerald-400 rounded-full" />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-sentio-gray">Neutral</span>
                <span className="text-gray-500 font-medium">21%</span>
              </div>
              <div className="h-2 bg-sentio-light rounded-full overflow-hidden">
                <div className="h-full w-[21%] bg-gray-400 rounded-full" />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-sentio-gray">Negative</span>
                <span className="text-red-500 font-medium">12%</span>
              </div>
              <div className="h-2 bg-sentio-light rounded-full overflow-hidden">
                <div className="h-full w-[12%] bg-gradient-to-r from-red-500 to-rose-400 rounded-full" />
              </div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-5 border border-sentio-border card-shadow">
          <p className="text-sm font-semibold text-sentio-dark mb-3">Top Topics</p>
          <div className="flex flex-wrap gap-2">
            {["Customer Service", "Pricing", "Quality", "Shipping", "Returns", "UI/UX"].map(
              (topic) => (
                <span
                  key={topic}
                  className="px-3 py-1.5 text-xs rounded-full bg-sentio-light border border-sentio-border text-sentio-gray font-medium"
                >
                  {topic}
                </span>
              )
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function TrustedBy() {
  const companies = ["Shopify", "Stripe", "Notion", "Linear", "Vercel", "Figma"];

  return (
    <section className="py-16 px-6 border-y border-sentio-border bg-sentio-light/50">
      <div className="max-w-7xl mx-auto">
        <p className="text-center text-sm text-sentio-gray mb-8">
          Trusted by forward-thinking companies
        </p>
        <div className="flex flex-wrap items-center justify-center gap-x-12 gap-y-6">
          {companies.map((company) => (
            <span key={company} className="text-xl font-semibold text-sentio-gray/40">
              {company}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}

function Features() {
  const features = [
    {
      icon: Database,
      title: "Vector-Powered Search",
      description:
        "Our semantic vector database captures the true meaning of every review, enabling natural language queries.",
    },
    {
      icon: MessageSquare,
      title: "Chat Interface",
      description:
        "Ask questions like you would to a colleague. Get instant answers backed by thousands of customer voices.",
    },
    {
      icon: TrendingUp,
      title: "Trend Detection",
      description:
        "Automatically surface emerging patterns and sentiment shifts before they become problems.",
    },
    {
      icon: Search,
      title: "Deep Insights",
      description:
        "Go beyond surface-level metrics. Understand the why behind customer sentiment.",
    },
    {
      icon: BarChart3,
      title: "Visual Analytics",
      description:
        "Beautiful dashboards that make complex data simple. Export reports in one click.",
    },
    {
      icon: Zap,
      title: "Real-Time Sync",
      description:
        "Connect your review sources and get insights updated automatically as new reviews arrive.",
    },
  ];

  return (
    <section id="features" className="py-24 px-6">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-4 text-sentio-dark">
            Why Teams Choose <span className="text-gradient">Sentio</span>
          </h2>
          <p className="text-sentio-gray text-lg max-w-2xl mx-auto">
            Everything you need to transform customer feedback into competitive advantage.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="group p-6 rounded-2xl bg-white border border-sentio-border card-shadow card-shadow-hover transition-all"
            >
              <div className="w-12 h-12 rounded-xl bg-sentio-blue/10 flex items-center justify-center mb-4 group-hover:bg-sentio-blue/20 transition-colors">
                <feature.icon className="w-6 h-6 text-sentio-blue" />
              </div>
              <h3 className="font-semibold text-xl mb-2 text-sentio-dark">{feature.title}</h3>
              <p className="text-sentio-gray">{feature.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

function HowItWorks() {
  const steps = [
    {
      number: "01",
      title: "Connect Your Sources",
      description: "Import reviews from any platform—App Store, Google Play, G2, Trustpilot, or your own database.",
    },
    {
      number: "02",
      title: "AI Processing",
      description: "Our vector engine analyzes and indexes every review, capturing semantic meaning and relationships.",
    },
    {
      number: "03",
      title: "Start Chatting",
      description: "Ask questions naturally and get instant, accurate insights backed by your actual customer data.",
    },
  ];

  return (
    <section id="how-it-works" className="py-24 px-6 bg-sentio-light/50">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-4 text-sentio-dark">
            Get Started in <span className="text-gradient">Minutes</span>
          </h2>
          <p className="text-sentio-gray text-lg max-w-2xl mx-auto">
            No complex setup. No data science degree required.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-8">
          {steps.map((step, index) => (
            <motion.div
              key={step.number}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.2 }}
              className="relative"
            >
              <div className="text-7xl font-bold text-sentio-blue/10 mb-4">
                {step.number}
              </div>
              <h3 className="font-semibold text-xl mb-2 text-sentio-dark">{step.title}</h3>
              <p className="text-sentio-gray">{step.description}</p>
              {index < steps.length - 1 && (
                <div className="hidden md:block absolute top-10 right-0 w-1/3 h-px bg-gradient-to-r from-sentio-blue/30 to-transparent" />
              )}
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

function ChatPreview() {
  const messages = [
    { role: "user", content: "What do customers love most about our product?" },
    {
      role: "assistant",
      content:
        "Based on 8,234 positive reviews, customers consistently praise three key areas: ease of use (mentioned in 72% of positive reviews), customer support responsiveness (64%), and value for money (58%).",
    },
    { role: "user", content: "Yes, tell me more about the ease of use feedback" },
    {
      role: "assistant",
      content:
        'Customers frequently use words like "intuitive", "simple", and "just works" when describing their experience. Key highlights include: one-click setup (412 mentions), clean interface (387 mentions), and helpful onboarding (298 mentions).',
    },
  ];

  return (
    <section className="py-24 px-6">
      <div className="max-w-7xl mx-auto">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-6 text-sentio-dark">
              Talk to Your <span className="text-gradient">Reviews</span>
            </h2>
            <p className="text-sentio-gray text-lg mb-8">
              No more endless scrolling through reviews. No more manual tagging or categorization.
              Just ask what you want to know.
            </p>
            <ul className="space-y-4">
              {[
                "Natural language understanding",
                "Context-aware responses",
                "Source citations for every insight",
                "Follow-up questions supported",
              ].map((item) => (
                <li key={item} className="flex items-center gap-3">
                  <div className="w-5 h-5 rounded-full bg-sentio-blue/10 flex items-center justify-center">
                    <Check className="w-3 h-3 text-sentio-blue" />
                  </div>
                  <span className="text-sentio-dark">{item}</span>
                </li>
              ))}
            </ul>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="rounded-2xl border border-sentio-border card-shadow bg-white p-1"
          >
            <div className="bg-sentio-light rounded-xl p-6">
              <div className="space-y-4">
                {messages.map((msg, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 10 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: index * 0.15 }}
                    className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                  >
                    <div
                      className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm ${
                        msg.role === "user"
                          ? "bg-gradient-to-r from-sentio-blue to-sentio-blue-light text-white"
                          : "bg-white border border-sentio-border text-sentio-dark"
                      }`}
                    >
                      {msg.content}
                    </div>
                  </motion.div>
                ))}
              </div>
              <div className="mt-4 flex items-center gap-3 p-3 rounded-xl bg-white border border-sentio-border">
                <input
                  type="text"
                  placeholder="Ask about your reviews..."
                  className="flex-1 bg-transparent outline-none text-sm placeholder:text-sentio-gray text-sentio-dark"
                />
                <button className="w-8 h-8 rounded-lg bg-gradient-to-r from-sentio-blue to-sentio-blue-light flex items-center justify-center">
                  <ArrowRight className="w-4 h-4 text-white" />
                </button>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}

function Pricing() {
  const plans = [
    {
      name: "Starter",
      price: "$49",
      description: "Perfect for small businesses",
      features: ["Up to 10,000 reviews", "5 team members", "Basic analytics", "Email support"],
      highlighted: false,
    },
    {
      name: "Pro",
      price: "$149",
      description: "For growing companies",
      features: [
        "Up to 100,000 reviews",
        "Unlimited team members",
        "Advanced analytics",
        "Priority support",
        "Custom integrations",
        "API access",
      ],
      highlighted: true,
    },
    {
      name: "Enterprise",
      price: "Custom",
      description: "For large organizations",
      features: [
        "Unlimited reviews",
        "Dedicated account manager",
        "Custom AI training",
        "SLA guarantee",
        "On-premise option",
        "White-label available",
      ],
      highlighted: false,
    },
  ];

  return (
    <section id="pricing" className="py-24 px-6 bg-sentio-light/50">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-4 text-sentio-dark">
            Simple, Transparent <span className="text-gradient">Pricing</span>
          </h2>
          <p className="text-sentio-gray text-lg max-w-2xl mx-auto">
            Start free. Upgrade when you&apos;re ready.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {plans.map((plan, index) => (
            <motion.div
              key={plan.name}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
              className={`relative rounded-2xl p-6 ${
                plan.highlighted
                  ? "bg-white border-2 border-sentio-blue card-shadow"
                  : "bg-white border border-sentio-border card-shadow"
              }`}
            >
              {plan.highlighted && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full bg-gradient-to-r from-sentio-blue to-sentio-blue-light text-xs font-medium text-white">
                  Most Popular
                </div>
              )}
              <h3 className="font-semibold text-xl mb-1 text-sentio-dark">{plan.name}</h3>
              <p className="text-sm text-sentio-gray mb-4">{plan.description}</p>
              <div className="mb-6">
                <span className="text-4xl font-bold text-sentio-dark">{plan.price}</span>
                {plan.price !== "Custom" && <span className="text-sentio-gray">/month</span>}
              </div>
              <ul className="space-y-3 mb-6">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-center gap-2 text-sm">
                    <Check className="w-4 h-4 text-sentio-blue" />
                    <span className="text-sentio-dark">{feature}</span>
                  </li>
                ))}
              </ul>
              <button
                className={`w-full py-3 rounded-xl font-medium transition-all ${
                  plan.highlighted
                    ? "btn-primary text-white"
                    : "border border-sentio-border hover:bg-sentio-light text-sentio-dark"
                }`}
              >
                {plan.price === "Custom" ? "Contact Sales" : "Start Free Trial"}
              </button>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

function CTA() {
  return (
    <section className="py-24 px-6">
      <div className="max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          className="rounded-3xl border border-sentio-border card-shadow bg-gradient-to-br from-sentio-blue/5 to-sentio-blue-light/5 p-12 text-center"
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-4 text-sentio-dark">
            Ready to Transform Your <span className="text-gradient">Customer Insights?</span>
          </h2>
          <p className="text-sentio-gray text-lg mb-8 max-w-2xl mx-auto">
            Join thousands of companies who&apos;ve stopped guessing and started understanding.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <button className="group px-8 py-4 rounded-full btn-primary text-white font-semibold text-lg flex items-center gap-2">
              Start Free Demo
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </button>
            <button className="px-8 py-4 rounded-full border border-sentio-border text-sentio-dark font-medium hover:bg-white transition-colors">
              Schedule a Call
            </button>
          </div>
          <div className="mt-8 flex flex-wrap items-center justify-center gap-6 text-sm text-sentio-gray">
            <span className="flex items-center gap-2">
              <Clock className="w-4 h-4" /> 5-minute setup
            </span>
            <span className="flex items-center gap-2">
              <Shield className="w-4 h-4" /> SOC 2 compliant
            </span>
            <span className="flex items-center gap-2">
              <Zap className="w-4 h-4" /> No credit card required
            </span>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer className="py-12 px-6 border-t border-sentio-border">
      <div className="max-w-7xl mx-auto">
        <div className="grid md:grid-cols-4 gap-8 mb-12">
          <div>
            <Image
              src="/sentio-logo.png"
              alt="Sentio"
              width={100}
              height={28}
              className="h-7 w-auto mb-4"
            />
            <p className="text-sentio-gray text-sm">
              AI-powered review intelligence that helps you understand your customers better.
            </p>
          </div>
          <div>
            <h4 className="font-semibold mb-4 text-sentio-dark">Product</h4>
            <ul className="space-y-2 text-sm text-sentio-gray">
              <li><a href="#" className="hover:text-sentio-dark transition-colors">Features</a></li>
              <li><a href="#" className="hover:text-sentio-dark transition-colors">Pricing</a></li>
              <li><a href="#" className="hover:text-sentio-dark transition-colors">Integrations</a></li>
              <li><a href="#" className="hover:text-sentio-dark transition-colors">API</a></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-4 text-sentio-dark">Company</h4>
            <ul className="space-y-2 text-sm text-sentio-gray">
              <li><a href="#" className="hover:text-sentio-dark transition-colors">About</a></li>
              <li><a href="#" className="hover:text-sentio-dark transition-colors">Blog</a></li>
              <li><a href="#" className="hover:text-sentio-dark transition-colors">Careers</a></li>
              <li><a href="#" className="hover:text-sentio-dark transition-colors">Contact</a></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-4 text-sentio-dark">Legal</h4>
            <ul className="space-y-2 text-sm text-sentio-gray">
              <li><a href="#" className="hover:text-sentio-dark transition-colors">Privacy</a></li>
              <li><a href="#" className="hover:text-sentio-dark transition-colors">Terms</a></li>
              <li><a href="#" className="hover:text-sentio-dark transition-colors">Security</a></li>
            </ul>
          </div>
        </div>
        <div className="pt-8 border-t border-sentio-border flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-sm text-sentio-gray">© 2026 Sentio. All rights reserved.</p>
          <div className="flex items-center gap-4">
            <a href="#" className="text-sentio-gray hover:text-sentio-dark transition-colors">Twitter</a>
            <a href="#" className="text-sentio-gray hover:text-sentio-dark transition-colors">LinkedIn</a>
            <a href="#" className="text-sentio-gray hover:text-sentio-dark transition-colors">GitHub</a>
          </div>
        </div>
      </div>
    </footer>
  );
}
