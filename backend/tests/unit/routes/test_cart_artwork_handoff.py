from server.routes.cart_routes import _has_confirmed_artwork_handoff


def test_artwork_handoff_requires_the_exact_supported_contract():
    assert _has_confirmed_artwork_handoff({
        'artworkHandoff': 'post_order_secure_transfer',
    })


def test_artwork_handoff_fails_closed_for_missing_or_untrusted_values():
    assert not _has_confirmed_artwork_handoff(None)
    assert not _has_confirmed_artwork_handoff({})
    assert not _has_confirmed_artwork_handoff({'artworkHandoff': 'uploaded_in_browser'})
    assert not _has_confirmed_artwork_handoff('post_order_secure_transfer')
