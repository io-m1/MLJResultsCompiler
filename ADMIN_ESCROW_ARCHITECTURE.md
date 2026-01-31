# Campus Market P2P: Admin-Mediated Escrow Architecture

**Version:** 1.0  
**Date:** January 30, 2026  
**Model:** Three-party escrow with admin as middleman  

---

## SYSTEM OVERVIEW

```
┌─────────────┐     Post Listing      ┌──────────────┐
│             │  (price: 50,000)      │              │
│   SELLER    │──────────────────────▶│    ADMIN     │
│             │                       │              │
└─────────────┘                       └──────────────┘
       ▲                                      ▲
       │                                      │
       │ Release Funds                        │ Approve + Add
       │ (45,000 NGN)                        │ Commission 15%
       │                                      │ (Total: 57,500 NGN)
       │                                      │
┌─────────────┐     DM / Chat      ┌──────────────┐
│             │◀─────────────────▶│              │
│   BUYER     │                    │              │
│             │  Payment Intent    │  ESCROW      │
└─────────────┘───────────────────▶│              │
               (57,500 NGN)         └──────────────┘
```

---

## WORKFLOW: COMPLETE TRANSACTION FLOW

### Stage 1: Post Submission & Approval

```
SELLER ACTION:
├─ Click "Sell Fast"
├─ Enter: Title, Description, Price (50,000 NGN)
├─ Upload Images (optional)
└─ Submit for Approval
    └─ Status: pending_approval
    └─ Stored in posts table

ADMIN ACTION:
├─ View posts.approval_queue
├─ Review content & images
├─ Decision: Approve OR Reject
│   └─ If Reject: post.status = rejected
│   └─ If Approve:
│       ├─ Add commission (15% = 7,500 NGN)
│       ├─ Create transaction record
│       ├─ Calculate: basePrice=50,000 + commission=7,500 = 57,500
│       ├─ Generate transaction hash
│       ├─ post.status = approved
│       └─ Post goes LIVE on marketplace

POST GOES LIVE:
└─ Visible to all users in Browse section
```

**Database State After Approval:**

```typescript
// posts table
{
  id: "post-123",
  seller_id: "seller-abc",
  title: "iPhone 13",
  price: 50000,           // Original price
  status: "approved",
  transaction_id: "tx-456"
}

// transactions table
{
  id: "tx-456",
  post_id: "post-123",
  seller_id: "seller-abc",
  buyer_id: null,         // Not yet assigned
  admin_id: "admin-xyz",
  base_price: 50000,
  admin_commission_percent: 15,
  admin_commission_amount: 7500,
  total_price: 57500,
  status: "approved",
  hash: "sha256(post-123-seller-abc-admin-xyz-50000-7500-57500)"
}
```

---

### Stage 2: Buyer Discovery & Interest

```
BUYER ACTION:
├─ Browse marketplace
├─ Click on approved post (iPhone 13)
├─ View:
│   ├─ Product details
│   ├─ TOTAL PRICE: 57,500 NGN (includes admin fee)
│   └─ Original seller price: 50,000 NGN
├─ Click "Message Seller" OR "Chat on WhatsApp"
│   └─ If WhatsApp: Direct to seller's WhatsApp
│   └─ If Platform DM: Go to Stage 2A

STAGE 2A: PLATFORM DM (Encrypted)
├─ Buyer sends: "Interested, is it still available?"
├─ Message stored ENCRYPTED in messages table
├─ Seller receives notification
└─ Conversation history encrypted in database
```

**Key Point:** Multiple buyers can message seller, but only one wins the bidding.

---

### Stage 3: Bidding & Admin Selection

```
SCENARIO: 3 buyers interested in iPhone 13

BUYER 1:
├─ Offers: 57,500 NGN (asking price)
└─ Ready to pay immediately

BUYER 2:
├─ Offers: 56,000 NGN (lower)
└─ Wants negotiation

BUYER 3:
├─ Offers: 58,000 NGN (higher)
└─ Wants to pay TODAY

ADMIN ACTION:
├─ Reviews all buyer offers
├─ Considers:
│   ├─ Buyer reliability (history)
│   ├─ Payment speed
│   ├─ Buyer reputation
│   └─ Platform profit (admin commission fixed at 7,500)
├─ Decision: Choose BUYER 3 (58,000 NGN)
│   └─ Higher total = better for seller + admin
│   └─ Buyer 3 has good history
│   └─ Ready to pay today
│
└─ Notify:
    ├─ SELLER: "Your iPhone listing approved. Buyer selected."
    ├─ BUYER 3: "Admin approved your purchase. Ready to pay?"
    └─ BUYER 1,2: "Another buyer selected. Want other listings?"
```

**Database Update After Admin Selection:**

```typescript
// transactions table
{
  id: "tx-456",
  post_id: "post-123",
  seller_id: "seller-abc",
  buyer_id: "buyer-charlie",  // NOW ASSIGNED
  admin_id: "admin-xyz",
  base_price: 50000,
  admin_commission_percent: 15,
  admin_commission_amount: 7500,
  total_price: 57500,         // or 58,000 if negotiated
  status: "buyer_assigned",
  assigned_at: "2025-01-30T14:00:00Z"
}

// Buyer acceptance
{
  buyer_acceptance: true,
  accepted_at: "2025-01-30T14:05:00Z",
  ready_to_pay: true
}
```

---

### Stage 4: Payment to Escrow

```
BUYER ACTION:
├─ Receives payment instruction (after admin selection)
├─ Admin provides account:
│   ├─ Account Name: "Campus Market P2P Escrow"
│   ├─ Bank: GTB
│   ├─ Account: 0102XXXXXXX
│   └─ Amount: 57,500 NGN (or negotiated amount)
│
├─ Transfers 57,500 NGN to admin account
├─ Screenshots payment proof
└─ Sends proof to admin (Encrypted DM)

ADMIN ACTION (After payment received):
├─ Verifies transfer in GTB account
├─ Checks amount matches transaction
├─ Creates escrow record:
│   ├─ escrow_accounts.status = "held"
│   ├─ Full 57,500 NGN locked
│   └─ Release pending seller confirmation
│
├─ Notifies SELLER:
│   └─ "Payment received. Admin holding funds."
│   └─ "Send product & confirm delivery for release"
│
└─ Notifies BUYER:
    └─ "Payment confirmed. Waiting for delivery."
```

**Escrow Record Created:**

```typescript
{
  id: "escrow-789",
  transaction_id: "tx-456",
  buyer_id: "buyer-charlie",
  admin_id: "admin-xyz",
  seller_id: "seller-abc",
  amount: 57500,
  admin_commission: 7500,
  seller_amount: 50000,
  payment_ref: "GTB-TRF-20250130-12345",
  status: "held",
  created_at: "2025-01-30T14:30:00Z"
}

// Breakdown in escrow:
{
  total_held: 57500,
  ├─ admin_commission: 7500,   // Already earned
  └─ seller_payout: 50000      // Pending delivery
}
```

---

### Stage 5: Product Delivery & Confirmation

```
SELLER ACTION:
├─ Receives notification: "Admin is holding payment"
├─ Ships/Delivers product to buyer
├─ Sends tracking (if shipping) or delivery proof
├─ Informs admin: "Product sent"
│   └─ Screenshot of tracking/proof
│   └─ Estimated delivery date
│
└─ Awaits buyer confirmation

BUYER ACTION (After receiving product):
├─ Inspects product
├─ Confirms:
│   ├─ Product received ✓
│   ├─ Condition matches description ✓
│   ├─ All items included ✓
│   └─ Ready to release payment ✓
│
├─ Notifies admin: "Product confirmed"
└─ Awaits fund release
```

---

### Stage 6: Fund Release from Escrow

```
ADMIN ACTION (After seller delivery confirmed):
├─ Verifies:
│   ├─ Payment received from buyer ✓
│   ├─ Seller delivered product ✓
│   ├─ Buyer confirmed receipt ✓
│   └─ Transaction hash valid ✓ (tamper check)
│
├─ Release funds:
│   ├─ SELLER: Transfer 50,000 NGN
│   └─ ADMIN: Keep 7,500 NGN commission
│
├─ Update escrow:
│   └─ escrow_accounts.status = "released"
│   └─ confirmation_proof = admin_signature
│   └─ released_at = timestamp
│
├─ Create payout log:
│   ├─ SELLER: 50,000 NGN pending
│   ├─ ADMIN: 7,500 NGN pending
│   └─ Both marked as "pending" until bank confirms
│
└─ Mark transaction:
    └─ transactions.status = "completed"

MONEY FLOW:
├─ BUYER paid: 57,500 NGN to admin account
│
├─ ADMIN releases:
│   ├─ 50,000 NGN → SELLER bank account
│   ├─ 7,500 NGN → ADMIN keeps (commission)
│   └─ 0 NGN → BUYER (already paid)
│
└─ SELLER receives: 50,000 NGN ✓
```

**Final State:**

```typescript
// transactions table
{
  id: "tx-456",
  status: "completed",
  completed_at: "2025-01-30T15:30:00Z",
  hash: "sha256(...)"  // Intact = no tampering
}

// escrow_accounts table
{
  id: "escrow-789",
  status: "released",
  released_at: "2025-01-30T15:30:00Z",
  confirmation_proof: "admin_signature_123"
}

// payout_logs table
[
  {
    id: "payout-1",
    transaction_id: "tx-456",
    recipient: "seller-abc",
    amount: 50000,
    type: "seller_payout",
    status: "processed",
    processed_at: "2025-01-30T15:31:00Z"
  },
  {
    id: "payout-2",
    transaction_id: "tx-456",
    recipient: "admin-xyz",
    amount: 7500,
    type: "admin_commission",
    status: "processed",
    processed_at: "2025-01-30T15:31:00Z"
  }
]
```

---

## SECURITY MEASURES

### 1. Transaction Integrity (Hash Verification)

```typescript
// No admin can modify post-approval transaction details
const transaction = {
  post_id: "post-123",
  seller_id: "seller-abc",
  admin_id: "admin-xyz",
  base_price: 50000,
  admin_commission: 7500,
  total_price: 57500
};

const hash = sha256(stringify(transaction));
// If ANY field changes → hash changes → tamper detected

// On release:
const storedHash = await getTransactionHash("tx-456");
const recalculatedHash = sha256(stringify(transaction));

if (storedHash !== recalculatedHash) {
  throw new Error("Transaction tampered. Release blocked.");
}
```

### 2. Role-Based Authorization

```typescript
// Only ADMIN can:
├─ Approve posts
├─ Assign buyers
├─ Release escrow funds
└─ Record commissions

// ADMIN CANNOT:
├─ Change their own commission % (hardcoded in system)
├─ Release without buyer confirmation
├─ Transfer funds to personal account
└─ Delete transaction records

// Enforce via RLS policies:
create policy "Only admins can approve posts"
  on posts for update
  using (
    (select is_admin from users where id = auth.uid()) = true
    and old.status = 'pending_approval'
  );
```

### 3. Escrow Lock-In

```typescript
// Once payment received:
├─ Funds in escrow_accounts.status = "held"
├─ NO ONE can manually withdraw
├─ Release only via:
│   ├─ Admin approval + seller confirmation
│   └─ Dispute resolution (future)
│
// Attempt unauthorized release → Audit log + Alert
```

### 4. Audit Trail

```sql
create table audit_logs (
  id uuid primary key,
  admin_id uuid not null,
  action varchar not null,  -- "approved_post", "released_escrow", etc.
  target_id uuid not null,  -- post_id, transaction_id, etc.
  before_state jsonb,
  after_state jsonb,
  timestamp timestamp default now()
);

-- Every critical action logged
```

---

## DISPUTE RESOLUTION (Future Enhancement)

```
IF BUYER says: "Product never arrived"
   └─ Transaction frozen
   └─ Admin investigates
   └─ Options:
       ├─ Confirm shipping proof → Release to seller
       ├─ No proof → Refund buyer
       └─ Partial refund (negotiated)

IF SELLER says: "Buyer claims defective, demands refund"
   └─ Admin reviews messages
   └─ Options:
       ├─ Photo proof of defect → Refund buyer
       └─ Buyer fault → Release to seller

IF BOTH agree on resolution
   └─ Admin executes split payout
   └─ Transaction marked "resolved_with_dispute"
```

---

## PHASE DIAGRAM: Complete Lifecycle

```
SUBMISSION
    ↓
[pending_approval] ──────────────────────────┐
    ↓                                         │
    └──────────────────────────────────────►│ [rejected] (SELLER notified)
                                             │
[approved] ◄──────────────────────────────────┘
    ↓
[live_on_marketplace]
    ↓
[buyer_interested]
    ↓
[admin_selects_buyer]
    ↓
[buyer_assigned]
    ↓
[buyer_accepts]
    ↓
[payment_received] ──────────────────────────┐
    ↓                                         │
[in_escrow]                                  │
    ↓                                         │ [payment_unconfirmed]
[seller_delivered]                           │
    ↓                                         │
[buyer_confirmed]                            │
    ↓                                         │
[ready_for_release]                          │
    ↓                                         │
[completed] ◄──────────────────────────────────┘
    ↓
[funds_disbursed]

TERMINAL STATES:
  ├─ completed (success)
  ├─ rejected (admin rejected post)
  ├─ cancelled (user cancelled)
  ├─ disputed (dispute ongoing)
  └─ refunded (buyer refunded)
```

---

## API ENDPOINTS

### Admin Approval
```
POST /api/admin/posts/{postId}/approve
{
  "commissionPercent": 15
}

RESPONSE:
{
  "success": true,
  "transactionId": "tx-456",
  "totalPrice": 57500
}

VALIDATION:
├─ User is admin ✓
├─ Post exists ✓
├─ Post status is pending_approval ✓
├─ Commission percent valid (5-25%) ✓
└─ Generate transaction hash ✓
```

### Record Payment
```
POST /api/admin/transactions/{txId}/payment-received
{
  "amount": 57500,
  "paymentRef": "GTB-TRF-20250130-12345"
}

RESPONSE:
{
  "success": true,
  "escrowId": "escrow-789",
  "status": "held"
}

VALIDATION:
├─ Admin is payer's admin ✓
├─ Amount matches transaction ✓
└─ Create escrow lock ✓
```

### Release Escrow
```
POST /api/admin/escrow/{escrowId}/release
{
  "confirmationProof": "admin_signature_xyz"
}

RESPONSE:
{
  "success": true,
  "sellerPayout": 50000,
  "adminCommission": 7500,
  "payoutsCreated": 2
}

VALIDATION:
├─ Admin authorized ✓
├─ Escrow status is "held" ✓
├─ Buyer confirmed delivery ✓
├─ Transaction hash valid ✓
└─ Create payout records ✓
```

---

## DATABASE SCHEMA

### Core Tables

```sql
-- Posts (user submissions)
CREATE TABLE posts (
  id UUID PRIMARY KEY,
  seller_id UUID NOT NULL REFERENCES users(id),
  title VARCHAR NOT NULL,
  description TEXT,
  price INTEGER NOT NULL,
  category VARCHAR,
  images TEXT[],
  status VARCHAR DEFAULT 'pending_approval',
  transaction_id UUID REFERENCES transactions(id),
  submitted_at TIMESTAMP,
  approved_at TIMESTAMP,
  rejected_at TIMESTAMP,
  rejected_reason TEXT
);

-- Transactions (financial records)
CREATE TABLE transactions (
  id UUID PRIMARY KEY,
  post_id UUID NOT NULL UNIQUE REFERENCES posts(id),
  seller_id UUID NOT NULL REFERENCES users(id),
  buyer_id UUID REFERENCES users(id),
  admin_id UUID NOT NULL REFERENCES users(id),
  base_price INTEGER NOT NULL,
  admin_commission_percent INTEGER NOT NULL,
  admin_commission_amount INTEGER NOT NULL,
  total_price INTEGER NOT NULL,
  status VARCHAR DEFAULT 'approved',
  hash VARCHAR(64) NOT NULL,
  approved_at TIMESTAMP,
  completed_at TIMESTAMP,
  
  CONSTRAINT check_prices 
    CHECK (total_price = base_price + admin_commission_amount)
);

-- Escrow (money holding)
CREATE TABLE escrow_accounts (
  id UUID PRIMARY KEY,
  transaction_id UUID NOT NULL UNIQUE REFERENCES transactions(id),
  buyer_id UUID NOT NULL REFERENCES users(id),
  admin_id UUID NOT NULL REFERENCES users(id),
  seller_id UUID NOT NULL REFERENCES users(id),
  amount INTEGER NOT NULL,
  admin_commission INTEGER NOT NULL,
  seller_amount INTEGER NOT NULL,
  payment_ref VARCHAR(100),
  status VARCHAR DEFAULT 'held',
  created_at TIMESTAMP,
  released_at TIMESTAMP,
  confirmation_proof TEXT,
  
  CONSTRAINT check_escrow_amounts 
    CHECK (amount = admin_commission + seller_amount)
);

-- Payouts
CREATE TABLE payout_logs (
  id UUID PRIMARY KEY,
  transaction_id UUID NOT NULL REFERENCES transactions(id),
  recipient UUID NOT NULL REFERENCES users(id),
  amount INTEGER NOT NULL,
  type VARCHAR(20) NOT NULL,  -- 'seller_payout', 'admin_commission'
  status VARCHAR DEFAULT 'pending',
  processed_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Messages (encrypted)
CREATE TABLE messages (
  id UUID PRIMARY KEY,
  conversation_id UUID NOT NULL,
  sender_id UUID NOT NULL REFERENCES users(id),
  ciphertext TEXT NOT NULL,
  iv VARCHAR NOT NULL,
  auth_tag VARCHAR NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Audit
CREATE TABLE audit_logs (
  id UUID PRIMARY KEY,
  admin_id UUID NOT NULL REFERENCES users(id),
  action VARCHAR NOT NULL,
  target_id UUID NOT NULL,
  before_state JSONB,
  after_state JSONB,
  timestamp TIMESTAMP DEFAULT NOW()
);
```

---

## SUMMARY

| Phase | Actor | Action | Status Field |
|-------|-------|--------|--------------|
| 1 | Seller | Submit for approval | `pending_approval` |
| 2 | Admin | Review & approve | `approved` |
| 3 | Buyer | Browse & message | `live` |
| 4 | Admin | Select buyer | `buyer_assigned` |
| 5 | Buyer | Transfer funds | `in_escrow` |
| 6 | Seller | Ship product | `seller_delivered` |
| 7 | Buyer | Confirm receipt | `buyer_confirmed` |
| 8 | Admin | Release funds | `completed` |

**Key Principle:** Admin is escrow agent, not marketplace owner. All money flows through admin account. Trust in admin is paramount.

---

**Document Version:** 1.0  
**Ready to Implement:** ✅ YES  
**Requires Admin Setup:** ✅ YES  
