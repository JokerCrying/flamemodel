"""
Test cases for HyperLogLog ORM model.

This file demonstrates various usage patterns of the HyperLogLog ORM.
"""
import pytest
from flamemodel.models import HyperLogLog
from flamemodel import fields


# ============================================================================
# Basic Usage Examples
# ============================================================================

class DailyUV(HyperLogLog):
    """Basic HLL model for daily unique visitor tracking."""
    __key_pattern__ = "stats:uv:daily:{date}"
    date: str = fields(primary_key=True)


class PageViewers(HyperLogLog):
    """Track unique viewers per page."""
    __key_pattern__ = "page:{page_id}:viewers"
    page_id: str = fields(primary_key=True)


class SearchTerms(HyperLogLog):
    """Track unique search terms."""
    __key_pattern__ = "search:unique_terms:{date}"
    date: str = fields(primary_key=True)


# ============================================================================
# Advanced Usage Examples
# ============================================================================

class HourlyUV(HyperLogLog):
    """Hourly UV tracking with time-bucketed pattern."""
    __key_pattern__ = "stats:uv:hourly:{date}:{hour}"
    date: str = fields(primary_key=True)
    hour: int


class CategoryPageUV(HyperLogLog):
    """Multi-dimensional UV tracking (category + page)."""
    __key_pattern__ = "category:{category}:page:{page_id}:uv"
    category: str = fields(primary_key=True)
    page_id: str


class IPTracker(HyperLogLog):
    """Track unique IPs accessing an API endpoint."""
    __key_pattern__ = "api:{endpoint}:unique_ips"
    endpoint: str = fields(primary_key=True)


# ============================================================================
# Test Cases
# ============================================================================

class TestHyperLogLogBasicOperations:
    """Test basic HLL operations."""
    
    def test_add_and_count(self):
        """Test adding elements and counting."""
        uv = DailyUV(date="2025-11-20")
        
        # Add single element
        result = uv.add("user_1")
        assert result in (0, 1)
        
        # Add multiple elements
        uv.add("user_2", "user_3", "user_4")
        
        # Count should be approximately 4
        count = uv.count()
        assert 3 <= count <= 5  # Allow for HLL error margin
        
        # Test len() support
        assert len(uv) == count
    
    def test_add_duplicate_elements(self):
        """Test that duplicates are properly handled."""
        uv = DailyUV(date="2025-11-20")
        
        # Add same user multiple times
        uv.add("user_1")
        uv.add("user_1")
        uv.add("user_1")
        
        # Count should still be 1
        assert uv.count() == 1
    
    def test_iadd_operator(self):
        """Test += operator support."""
        uv = DailyUV(date="2025-11-20")
        
        # Add using +=
        uv += ["user_1", "user_2"]
        uv += ["user_3", "user_4"]
        
        count = uv.count()
        assert 3 <= count <= 5
    
    def test_class_level_operations(self):
        """Test class-level add and count operations."""
        # Add using class method
        DailyUV.add_to("2025-11-21", "user_10", "user_11", "user_12")
        
        # Count using class method
        count = DailyUV.count_by_pk("2025-11-21")
        assert 2 <= count <= 4


class TestHyperLogLogMergeOperations:
    """Test HLL merge operations."""
    
    def test_merge_from_instances(self):
        """Test merging from other instances."""
        # Create separate HLLs for different pages
        page1 = PageViewers(page_id="page1")
        page1.add("user_1", "user_2")
        
        page2 = PageViewers(page_id="page2")
        page2.add("user_2", "user_3")  # user_2 overlaps
        
        # Merge into total
        total = PageViewers(page_id="total")
        total.merge_from(page1, page2)
        
        # Total should be ~3 (user_1, user_2, user_3)
        count = total.count()
        assert 2 <= count <= 4
    
    def test_merge_by_pks(self):
        """Test merging multiple HLLs by primary keys."""
        # Add data to different days
        DailyUV.add_to("2025-11-14", "user_1", "user_2")
        DailyUV.add_to("2025-11-15", "user_2", "user_3")
        DailyUV.add_to("2025-11-16", "user_3", "user_4")
        
        # Merge to get weekly UV
        weekly_uv = DailyUV.merge_by_pks(
            pks=["2025-11-14", "2025-11-15", "2025-11-16"],
            auto_cleanup=True
        )
        
        # Should be ~4 unique users
        assert 3 <= weekly_uv <= 5
    
    def test_merge_to_key_with_expiration(self):
        """Test merging to a specific key with TTL."""
        # Add data
        HourlyUV.add_to("2025-11-20:00", "user_1", "user_2")
        HourlyUV.add_to("2025-11-20:01", "user_2", "user_3")
        
        # Merge with expiration
        dest_key = HourlyUV.merge_to_key(
            dest_key="temp:hourly:merge:001",
            pks=["2025-11-20:00", "2025-11-20:01"],
            expire_seconds=3600
        )
        
        # Count from merged key
        count = HourlyUV.count_by_key(dest_key)
        assert 2 <= count <= 4
    
    def test_union_count(self):
        """Test union count without persisting."""
        # Add data to different categories
        CategoryPageUV.add_to("electronics:phone", "user_1", "user_2")
        CategoryPageUV.add_to("electronics:laptop", "user_2", "user_3")
        CategoryPageUV.add_to("books:novel", "user_4")
        
        # Get union count
        total = CategoryPageUV.union_count(
            "electronics:phone",
            "electronics:laptop",
            "books:novel"
        )
        
        # Should be ~4 unique users
        assert 3 <= total <= 5


class TestHyperLogLogAdvancedPatterns:
    """Test advanced usage patterns."""
    
    def test_time_bucketed_aggregation(self):
        """Test time-bucketed pattern with hourly data."""
        date = "2025-11-20"
        
        # Simulate 24 hours of data
        for hour in range(24):
            uv = HourlyUV(date=date, hour=hour)
            uv.add(f"user_{hour}", f"user_{hour + 1}")
        
        # Aggregate full day
        pk_list = [f"{date}:{hour:02d}" for hour in range(24)]
        daily_total = HourlyUV.merge_by_pks(pks=pk_list, auto_cleanup=True)
        
        # Should have some reasonable count
        assert daily_total > 0
    
    def test_multi_dimensional_tracking(self):
        """Test multi-dimensional tracking pattern."""
        # Track viewers across categories and pages
        cat_page = CategoryPageUV(category="tech", page_id="article_123")
        cat_page.add("viewer_1", "viewer_2", "viewer_3")
        
        count = cat_page.count()
        assert count == 3
    
    def test_api_ip_tracking(self):
        """Test API IP tracking use case."""
        tracker = IPTracker(endpoint="/api/users")
        
        # Simulate requests from different IPs
        ips = [
            "192.168.1.1",
            "192.168.1.2",
            "192.168.1.1",  # Duplicate
            "10.0.0.1",
            "10.0.0.2"
        ]
        
        for ip in ips:
            tracker.add(ip)
        
        # Should count 4 unique IPs
        unique_ips = tracker.count()
        assert unique_ips == 4


class TestHyperLogLogEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_hll(self):
        """Test empty HLL behavior."""
        uv = DailyUV(date="2025-11-30")
        assert uv.count() == 0
        assert len(uv) == 0
    
    def test_add_no_elements(self):
        """Test adding no elements."""
        uv = DailyUV(date="2025-11-30")
        result = uv.add()
        assert result == 0
    
    def test_merge_empty_list(self):
        """Test merging with empty list."""
        result = DailyUV.merge_by_pks(pks=[], auto_cleanup=True)
        assert result == 0
    
    def test_save_raises_error(self):
        """Test that save() raises NotImplementedError."""
        uv = DailyUV(date="2025-11-30")
        
        with pytest.raises(NotImplementedError) as exc_info:
            uv.save()
        
        assert "does not support save()" in str(exc_info.value)
    
    def test_large_scale_cardinality(self):
        """Test with large number of elements."""
        uv = DailyUV(date="2025-11-30")
        
        # Add 10000 unique elements
        elements = [f"user_{i}" for i in range(10000)]
        uv.add(*elements)
        
        count = uv.count()
        # HLL should estimate ~10000 with acceptable error
        assert 9900 <= count <= 10100  # ~1% error margin


# ============================================================================
# Real-World Usage Examples
# ============================================================================

class TestRealWorldScenarios:
    """Test real-world usage scenarios."""
    
    def test_weekly_uv_report(self):
        """
        Scenario: Generate weekly UV report from daily data.
        """
        # Simulate 7 days of UV data
        daily_data = {
            "2025-11-14": ["user_1", "user_2", "user_3"],
            "2025-11-15": ["user_2", "user_4", "user_5"],
            "2025-11-16": ["user_3", "user_6"],
            "2025-11-17": ["user_7", "user_8"],
            "2025-11-18": ["user_1", "user_9"],
            "2025-11-19": ["user_10"],
            "2025-11-20": ["user_2", "user_11", "user_12"]
        }
        
        # Load daily data
        for date, users in daily_data.items():
            DailyUV.add_to(date, *users)
        
        # Calculate weekly UV (with deduplication)
        weekly_uv = DailyUV.merge_by_pks(
            pks=list(daily_data.keys()),
            auto_cleanup=True
        )
        
        # Should count 12 unique users
        assert 11 <= weekly_uv <= 13
    
    def test_ab_test_unique_users(self):
        """
        Scenario: A/B test - count unique users in each variant.
        """
        class ABTestUV(HyperLogLog):
            __key_pattern__ = "ab_test:{experiment_id}:variant:{variant}:uv"
            experiment_id: str = fields(primary_key=True)
            variant: str
        
        # Track users in variant A
        variant_a = ABTestUV(experiment_id="exp_001", variant="A")
        variant_a.add("user_1", "user_2", "user_3")
        
        # Track users in variant B
        variant_b = ABTestUV(experiment_id="exp_001", variant="B")
        variant_b.add("user_4", "user_5")
        
        # Compare
        count_a = variant_a.count()
        count_b = variant_b.count()
        
        assert count_a == 3
        assert count_b == 2
    
    def test_funnel_unique_users(self):
        """
        Scenario: Track unique users at each funnel stage.
        """
        class FunnelStage(HyperLogLog):
            __key_pattern__ = "funnel:{funnel_id}:stage:{stage}:users"
            funnel_id: str = fields(primary_key=True)
            stage: str
        
        # Stage 1: Landing page
        landing = FunnelStage(funnel_id="checkout", stage="landing")
        landing.add("user_1", "user_2", "user_3", "user_4", "user_5")
        
        # Stage 2: Add to cart
        add_cart = FunnelStage(funnel_id="checkout", stage="add_cart")
        add_cart.add("user_1", "user_2", "user_3")
        
        # Stage 3: Purchase
        purchase = FunnelStage(funnel_id="checkout", stage="purchase")
        purchase.add("user_1", "user_2")
        
        # Calculate conversion rates
        landing_count = landing.count()
        cart_count = add_cart.count()
        purchase_count = purchase.count()
        
        assert landing_count == 5
        assert cart_count == 3
        assert purchase_count == 2
        
        cart_rate = cart_count / landing_count
        purchase_rate = purchase_count / cart_count
        
        assert 0 < cart_rate <= 1
        assert 0 < purchase_rate <= 1
