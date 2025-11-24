from src.flamemodel import HyperLogLog, fields, FlameModel


class DailyUV(HyperLogLog):
    """Track daily unique visitors."""
    __key_pattern__ = "stats:uv:daily:{date}"
    date: str = fields(primary_key=True)


def example_basic_uv_tracking():
    """Basic usage: track daily UV."""
    print("\n=== Example 1: Basic UV Tracking ===")

    # Create UV tracker for today
    uv_today = DailyUV(date="2025-11-20")

    # Simulate user visits
    uv_today.add("user_123")
    uv_today.add("user_456")
    uv_today.add("user_789")
    uv_today.add("user_123")  # Duplicate - will be counted once

    # Get UV count
    total_uv = uv_today.count()
    print(f"Today's UV: {total_uv}")  # Output: 3

    # Pythonic way
    print(f"Today's UV (Pythonic): {len(uv_today)}")


# ============================================================================
# Example 2: Time-Bucketed Aggregation
# ============================================================================

class HourlyUV(HyperLogLog):
    """Track UV per hour."""
    __key_pattern__ = "stats:uv:hourly:{date}:{hour:02d}"
    date: str = fields(primary_key=True)
    hour: int = fields()


def example_time_bucketed_aggregation():
    """Time-based aggregation: merge hourly data to get daily total."""
    print("\n=== Example 2: Time-Bucketed Aggregation ===")

    date = "2025-11-20"

    # Record hourly UV
    for hour in range(9, 18):  # 9am to 5pm
        hourly_uv = HourlyUV(date=date, hour=hour)
        # Simulate traffic
        hourly_uv.add(f"user_{hour}_1", f"user_{hour}_2", "regular_user")

    # Aggregate: get daily total from hourly data
    hourly_pks = [f"{date}:{hour:02d}" for hour in range(9, 18)]
    daily_total = HourlyUV.merge_by_pks(pks=hourly_pks, auto_cleanup=True)

    print(f"Daily UV (aggregated from hourly): {daily_total}")


# ============================================================================
# Example 3: Multi-Page UV Tracking
# ============================================================================

class PageUV(HyperLogLog):
    """Track UV per page."""
    __key_pattern__ = "page:{page_id}:uv:{date}"
    page_id: str = fields(primary_key=True)
    date: str = fields()


def example_multi_page_uv():
    """Track UV across multiple pages."""
    print("\n=== Example 3: Multi-Page UV ===")

    date = "2025-11-20"

    # Homepage visitors
    home_uv = PageUV(page_id="home", date=date)
    home_uv.add("user_1", "user_2", "user_3", "user_4", "user_5")

    # Product page visitors
    product_uv = PageUV(page_id="product_123", date=date)
    product_uv.add("user_2", "user_3", "user_6", "user_7")  # Some overlap

    # About page visitors
    about_uv = PageUV(page_id="about", date=date)
    about_uv.add("user_8", "user_9")

    print(f"Homepage UV: {home_uv.count()}")
    print(f"Product page UV: {product_uv.count()}")
    print(f"About page UV: {about_uv.count()}")

    # Calculate site-wide UV (union of all pages)
    site_wide_uv = PageUV.union_count(
        f"home:{date}",
        f"product_123:{date}",
        f"about:{date}"
    )
    print(f"Site-wide UV: {site_wide_uv}")


# ============================================================================
# Example 4: Weekly Report with Persistent Merge
# ============================================================================

def example_weekly_report():
    """Generate weekly report with persistent merge key."""
    print("\n=== Example 4: Weekly Report ===")

    # Simulate a week of data
    week_dates = [
        "2025-11-14", "2025-11-15", "2025-11-16", "2025-11-17",
        "2025-11-18", "2025-11-19", "2025-11-20"
    ]

    # Add daily data
    for i, date in enumerate(week_dates):
        DailyUV.add_to(date, *[f"user_{i}_{j}" for j in range(100)])

    # Create persistent weekly merge (expires in 24 hours)
    weekly_key = DailyUV.merge_to_key(
        dest_key="stats:uv:weekly:2025-W47",
        pks=week_dates,
        expire_seconds=86400  # 24 hours
    )

    # Query multiple times without re-merging
    weekly_uv = DailyUV.count_by_key(weekly_key)
    print(f"Weekly UV (2025-W47): {weekly_uv}")

    # Can query again without cost
    weekly_uv_again = DailyUV.count_by_key(weekly_key)
    print(f"Queried again: {weekly_uv_again}")


# ============================================================================
# Example 5: Funnel Analysis
# ============================================================================

class FunnelStage(HyperLogLog):
    """Track unique users at each funnel stage."""
    __key_pattern__ = "funnel:{funnel_id}:stage:{stage}:users"
    funnel_id: str = fields(primary_key=True)
    stage: str = fields()


def example_funnel_analysis():
    """Track and analyze conversion funnel."""
    print("\n=== Example 5: Funnel Analysis ===")

    funnel_id = "purchase_flow"

    # Stage 1: Product view
    view_stage = FunnelStage(funnel_id=funnel_id, stage="view")
    view_stage += [f"user_{i}" for i in range(1000)]

    # Stage 2: Add to cart
    cart_stage = FunnelStage(funnel_id=funnel_id, stage="add_cart")
    cart_stage += [f"user_{i}" for i in range(300)]

    # Stage 3: Checkout
    checkout_stage = FunnelStage(funnel_id=funnel_id, stage="checkout")
    checkout_stage += [f"user_{i}" for i in range(150)]

    # Stage 4: Payment
    payment_stage = FunnelStage(funnel_id=funnel_id, stage="payment")
    payment_stage += [f"user_{i}" for i in range(100)]

    # Calculate metrics
    view_count = view_stage.count()
    cart_count = cart_stage.count()
    checkout_count = checkout_stage.count()
    payment_count = payment_stage.count()

    print(f"Views: {view_count}")
    print(f"Add to Cart: {cart_count} ({cart_count / view_count * 100:.1f}%)")
    print(f"Checkout: {checkout_count} ({checkout_count / cart_count * 100:.1f}%)")
    print(f"Payment: {payment_count} ({payment_count / checkout_count * 100:.1f}%)")


# ============================================================================
# Example 6: A/B Test Tracking
# ============================================================================

class ABTestUV(HyperLogLog):
    """Track unique users in A/B test variants."""
    __key_pattern__ = "experiment:{exp_id}:variant:{variant}:users"
    exp_id: str = fields(primary_key=True)
    variant: str = fields()


def example_ab_test():
    """Track A/B test participants."""
    print("\n=== Example 6: A/B Test ===")

    exp_id = "homepage_redesign"

    # Control group (variant A)
    control = ABTestUV(exp_id=exp_id, variant="A")
    control += [f"user_{i}" for i in range(1, 501)]

    # Treatment group (variant B)
    treatment = ABTestUV(exp_id=exp_id, variant="B")
    treatment += [f"user_{i}" for i in range(501, 1001)]

    print(f"Control group size: {control.count()}")
    print(f"Treatment group size: {treatment.count()}")

    # Calculate total experiment participants
    total = ABTestUV.union_count(f"{exp_id}:A", f"{exp_id}:B")
    print(f"Total participants: {total}")


# ============================================================================
# Example 7: API Rate Limiting / IP Tracking
# ============================================================================

class APIUniqueIPs(HyperLogLog):
    """Track unique IPs accessing an API endpoint."""
    __key_pattern__ = "api:{endpoint}:unique_ips:{date}"
    endpoint: str = fields(primary_key=True)
    date: str = fields()


def example_api_ip_tracking():
    """Track unique IPs for API monitoring."""
    print("\n=== Example 7: API IP Tracking ===")

    endpoint = "/api/v1/users"
    date = "2025-11-20"

    ip_tracker = APIUniqueIPs(endpoint=endpoint, date=date)

    # Simulate API requests from different IPs
    requests = [
        "192.168.1.1",
        "192.168.1.2",
        "192.168.1.1",  # Repeat
        "10.0.0.1",
        "10.0.0.2",
        "192.168.1.1",  # Repeat again
        "172.16.0.1",
    ]

    for ip in requests:
        ip_tracker.add(ip)

    unique_ips = ip_tracker.count()
    print(f"Total requests: {len(requests)}")
    print(f"Unique IPs: {unique_ips}")


# ============================================================================
# Example 8: Search Term Deduplication
# ============================================================================

class UniqueSearchTerms(HyperLogLog):
    """Track unique search terms."""
    __key_pattern__ = "search:unique_terms:{date}"
    date: str = fields(primary_key=True)


def example_search_deduplication():
    """Track unique search terms per day."""
    print("\n=== Example 8: Search Term Deduplication ===")

    date = "2025-11-20"
    search_tracker = UniqueSearchTerms(date=date)

    # Simulate search queries (with duplicates)
    searches = [
        "python tutorial",
        "redis orm",
        "python tutorial",  # Duplicate
        "hyperloglog",
        "redis orm",  # Duplicate
        "data structures",
        "python tutorial",  # Duplicate
    ]

    for term in searches:
        search_tracker.add(term)

    print(f"Total searches: {len(searches)}")
    print(f"Unique search terms: {search_tracker.count()}")


# ============================================================================
# Example 9: Cross-Platform User Tracking
# ============================================================================

class PlatformUsers(HyperLogLog):
    """Track users across different platforms."""
    __key_pattern__ = "platform:{platform}:users:{date}"
    platform: str = fields(primary_key=True)
    date: str = fields()


def example_cross_platform_tracking():
    """Track users across web, iOS, Android."""
    print("\n=== Example 9: Cross-Platform Tracking ===")

    date = "2025-11-20"

    # Web users
    web = PlatformUsers(platform="web", date=date)
    web += [f"user_{i}" for i in range(1, 301)]

    # iOS users (some overlap with web)
    ios = PlatformUsers(platform="ios", date=date)
    ios += [f"user_{i}" for i in range(200, 501)]

    # Android users (some overlap)
    android = PlatformUsers(platform="android", date=date)
    android += [f"user_{i}" for i in range(400, 701)]

    print(f"Web users: {web.count()}")
    print(f"iOS users: {ios.count()}")
    print(f"Android users: {android.count()}")

    # Total unique users (cross-platform deduplicated)
    total_users = PlatformUsers.union_count(
        f"web:{date}",
        f"ios:{date}",
        f"android:{date}"
    )
    print(f"Total unique users (all platforms): {total_users}")


# ============================================================================
# Example 10: Using Operators
# ============================================================================

def example_pythonic_operators():
    """Demonstrate Pythonic operator usage."""
    print("\n=== Example 10: Pythonic Operators ===")

    uv = DailyUV(date="2025-11-20")

    # Use += operator
    uv += ["user_1", "user_2"]
    print(f"After first +=: {len(uv)}")

    # Use += again
    uv += ["user_3", "user_4", "user_5"]
    print(f"After second +=: {len(uv)}")

    # Use len()
    print(f"Total UV (using len()): {len(uv)}")


# ============================================================================
# Example 11: Custom Merge Strategy
# ============================================================================

def example_custom_merge_strategy():
    """Advanced: custom merge with manual control."""
    print("\n=== Example 11: Custom Merge Strategy ===")

    # Scenario: Merge data from multiple sources with custom logic

    # Source 1: Mobile app
    mobile = PageUV(page_id="mobile_home", date="2025-11-20")
    mobile += [f"user_{i}" for i in range(100)]

    # Source 2: Web app
    web = PageUV(page_id="web_home", date="2025-11-20")
    web += [f"user_{i}" for i in range(50, 150)]

    # Source 3: Desktop app
    desktop = PageUV(page_id="desktop_home", date="2025-11-20")
    desktop += [f"user_{i}" for i in range(100, 200)]

    # Custom merge: create a long-lived aggregation
    agg_key = "aggregated:all_platforms:home:2025-11-20"
    PageUV.merge_to_key(
        dest_key=agg_key,
        pks=["mobile_home:2025-11-20", "web_home:2025-11-20", "desktop_home:2025-11-20"],
        expire_seconds=7200  # 2 hours
    )

    # Query the aggregated result
    total = PageUV.count_by_key(agg_key)
    print(f"Total users across all platforms: {total}")


# ============================================================================
# Main Execution
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("HyperLogLog ORM Examples")
    fm = FlameModel(
        runtime_mode='sync',
        endpoint='redis://:@localhost:6379/1'
    )
    print('FlameModel init success')
    print("=" * 60)

    # Run all examples
    example_basic_uv_tracking()
    example_time_bucketed_aggregation()
    example_multi_page_uv()
    example_weekly_report()
    example_funnel_analysis()
    example_ab_test()
    example_api_ip_tracking()
    example_search_deduplication()
    example_cross_platform_tracking()
    example_pythonic_operators()
    example_custom_merge_strategy()

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)
