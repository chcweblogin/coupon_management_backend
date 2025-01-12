from django.urls import path
from .views import (
    BonusSettlementView,
    CheckAuthStatus,
    CouponRedeemViewSet,
    CreditsAPIView,
    CurrentStockAPIView,
    DoctorLastUpdate,
    FreeSamplesByDoctorAPIViewSet,
    GiftSettledAPIViewSet,
    RedeemProductByDoctorAPIView,
    RedeemableProductsView,
    RegisterView,
    LoginView,
    LogoutView,
    ProductListView,
    SettledStockAPIView,
    SettlementViewSet,
    TransactionDetailViewSet,
    TransactionViewSet,
    UserPersonalInfoView,
    VSOAnalysisAPIView,
    VSOCreation,
    VSOList,
    VSOManagerAnalysisAPIView,
    VSOMonthPerformanceAPIView,
    VSOSearchAPIView,
    VSOUpdateDelete,
    DoctorListCreate,
    DoctorDetail,
    ProductListCreate,
    ProductDetail,
    CouponListCreate,
    CouponDetail,
    CouponAPIView,
    TransactionAPIView,
    SettlementAPIView,
 
)


transaction_list = TransactionViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

transaction_detail = TransactionViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'delete': 'destroy'
})

transaction_detail_list = TransactionDetailViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

transaction_detail_item = TransactionDetailViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'delete': 'destroy'
})


settlement_viewset = SettlementViewSet.as_view({
    'get': 'list',           # GET /settlements/
    'post': 'create',        # POST /settlements/
    'get': 'retrieve',       # GET /settlements/{id}/
    'put': 'update',         # PUT /settlements/{id}/
    'patch': 'partial_update',# PATCH /settlements/{id}/
    'delete': 'destroy',     # DELETE /settlements/{id}/
})

coupon_redeem_list = CouponRedeemViewSet.as_view({
    'post': 'create'
})

urlpatterns = [
    # Authentication Routes
    path('check-auth-status/', CheckAuthStatus.as_view(), name='check_auth_status'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    

    # Product Routes
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/create/', ProductListCreate.as_view(), name='product-create'),
    path('products/<int:id>/', ProductDetail.as_view(), name='product-detail'),
    path('products/redeemable/', RedeemableProductsView.as_view(), name='redeemable-products'),

    # VSO (Sales Voice Officer) Routes
    path('vso/', VSOList.as_view(), name='vso-list'),
    path('create-vso-profile/', VSOCreation.as_view(), name='create-vso-profile'),
    path('create-vso-profile/', VSOUpdateDelete.as_view(), name='create-vso-profile'),

    path('vso/<str:vso_id>/', VSOUpdateDelete.as_view(), name='vso-update-delete'),
    path('analysis/', VSOAnalysisAPIView.as_view(), name='vso-analysis'),
    path('Manager/analysis/', VSOManagerAnalysisAPIView.as_view(), name='vso-analysis'),
    path('month-performance/', VSOMonthPerformanceAPIView.as_view(), name='vso-analysis-of-month'),

    # Get User Personal info
    path('api/user-info/', UserPersonalInfoView.as_view(), name='user-info'),
    
    # Doctor Routes
    path('doctors/', DoctorListCreate.as_view(), name='doctor-list-create'),
    path('doctors/<str:doctor_id>/', DoctorDetail.as_view(), name='doctor-detail'),
    path('search-doctor/', VSOSearchAPIView.as_view(), name='vso-search-doctor'),
    path('create-doctor-profile/', DoctorListCreate.as_view(), name='create-doctor-profile'),

    path('doctor-last-vist/', DoctorLastUpdate.as_view(), name='doctor-last-vist'),
    


    # Coupon Routes
    path('coupons/', CouponListCreate.as_view(), name='coupon-list-create'),
    path('coupons/<int:id>/', CouponDetail.as_view(), name='coupon-detail'),
    path('coupons/api/', CouponAPIView.as_view(), name='coupon-api'),
    path('coupons/redeem/', coupon_redeem_list, name='coupon-redeem'),


    #Credits Records Routes
    path('doctor-credits/', CreditsAPIView.as_view(), name='doctor-points-list'),

    # Transaction Routes
    path('transactions/', TransactionAPIView.as_view(), name='transaction-list'),
    path('transactions/<int:pk>/', transaction_detail, name='transaction-detail'),
    
    # Transaction Detail Routes
    path('transaction-details/', transaction_detail_list, name='transaction-detail-list'),
    path('transaction-details/<int:pk>/', transaction_detail_item, name='transaction-detail-item'),

    # Settlement Routes
    path('settlements/<int:pk>/', settlement_viewset, name='settlement-detail'),
    
        #Free Sample Routes
        path('settlements/samples/', FreeSamplesByDoctorAPIViewSet.as_view(), name='settlement-list'),
        path('settlements/gifts/', GiftSettledAPIViewSet.as_view(), name='gifts-list'),
        path('settlements/', SettlementAPIView.as_view(), name='settlement-list'),
    
        path('settlements/by-doctor/', RedeemProductByDoctorAPIView.as_view(), name='settlement-by-doctor'),

        
        
    
    path('settled-product-stock/', SettledStockAPIView.as_view(), name='redeemed-products'),
    path('current-product-stock/', CurrentStockAPIView.as_view(), name='collected-products'),
    
    path('bonus-settlements/', BonusSettlementView.as_view(), name='bonus-settlement-detail'),


    

]
