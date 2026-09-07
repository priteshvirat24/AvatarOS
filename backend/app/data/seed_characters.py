from backend.app.models.dna import (
    DigitalDNA, IdentitySpec, PersonalityVector, SpeechSpec,
    TopicsSpec, GestureProfile, BrandBinding
)
from backend.app.models.rights import RightsRecord

def get_seed_characters():
    maya_1_7 = DigitalDNA(
        character_id="maya",
        version="1.7.0",
        status="active",
        identity=IdentitySpec(
            face_embedding_ref="vault://identity/maya/face-v3.emb",
            face_embedding_model="arcface-r100-ir",
            similarity_threshold=0.92,
            voice_model_id="maya-english-v4",
            voice_similarity_threshold=0.90,
            reference_media=["gs://avataros-vault/maya/refs/angle_front.mp4"]
        ),
        personality_vector=PersonalityVector(
            confident=0.81,
            witty=0.64,
            analytical=0.77,
            warmth=0.55,
            formality=0.30,
            assertiveness=0.68
        ),
        speech=SpeechSpec(
            sentence_length="short",
            pace_multiplier=1.02,
            accent="indian_english",
            filler_words="minimal"
        ),
        topics=TopicsSpec(
            allowed=["technology", "startups", "product_education", "developer_tooling"],
            restricted=["financial_advice", "political_endorsement", "medical_claims"],
            on_restricted_hit="deflect_and_log"
        ),
        gesture_profile=GestureProfile(
            expressiveness=0.78,
            gesture_library="confident_technical_v2"
        ),
        brand=BrandBinding(
            org_id="example_co",
            brand_kit_ref="vault://brand/example_co/v9",
            primary_color="#6366F1",
            font_family="Outfit, sans-serif"
        ),
        rights_ref="rights://maya/authorization-2026-04",
        parent_version="1.6.0",
        changed_fields=["topics.allowed", "speech.pace_multiplier", "gesture_profile.expressiveness"],
        created_by="evolution_agent",
        created_at="2026-08-14T09:12:00Z"
    ).seal()

    maya_1_0 = DigitalDNA(
        character_id="maya",
        version="1.0.0",
        status="active",
        identity=IdentitySpec(
            face_embedding_ref="vault://identity/maya/face-v1.emb",
            face_embedding_model="arcface-r100-ir",
            similarity_threshold=0.92,
            voice_model_id="maya-english-v1",
            voice_similarity_threshold=0.90,
            reference_media=[]
        ),
        personality_vector=PersonalityVector(
            confident=0.75,
            witty=0.50,
            analytical=0.70,
            warmth=0.60,
            formality=0.40,
            assertiveness=0.60
        ),
        speech=SpeechSpec(
            sentence_length="short",
            pace_multiplier=1.00,
            accent="indian_english",
            filler_words="minimal"
        ),
        topics=TopicsSpec(
            allowed=["technology", "startups", "product_education"],
            restricted=["financial_advice", "political_endorsement", "medical_claims"],
            on_restricted_hit="deflect_and_log"
        ),
        gesture_profile=GestureProfile(
            expressiveness=0.62,
            gesture_library="confident_technical_v1"
        ),
        brand=BrandBinding(
            org_id="example_co",
            brand_kit_ref="vault://brand/example_co/v1"
        ),
        rights_ref="rights://maya/authorization-2026-04",
        parent_version=None,
        created_by="character_compiler",
        created_at="2026-06-01T10:00:00Z"
    ).seal()

    aria = DigitalDNA(
        character_id="aria",
        version="1.2.0",
        status="active",
        identity=IdentitySpec(
            face_embedding_ref="vault://identity/aria/face-v2.emb",
            voice_model_id="aria-global-v2"
        ),
        personality_vector=PersonalityVector(
            confident=0.88, witty=0.45, analytical=0.82, warmth=0.65, formality=0.55, assertiveness=0.75
        ),
        speech=SpeechSpec(sentence_length="medium", pace_multiplier=1.05, accent="american_standard"),
        topics=TopicsSpec(allowed=["enterprise_saas", "b2b_sales", "roi_calculators"], restricted=["competitor_disparagement"]),
        gesture_profile=GestureProfile(expressiveness=0.65, gesture_library="executive_presenter"),
        brand=BrandBinding(org_id="example_co"),
        rights_ref="rights://aria/auth-2026"
    ).seal()

    david = DigitalDNA(
        character_id="david",
        version="2.0.1",
        status="active",
        identity=IdentitySpec(
            face_embedding_ref="vault://identity/david/face-v2.emb",
            voice_model_id="david-uk-v2"
        ),
        personality_vector=PersonalityVector(
            confident=0.90, witty=0.35, analytical=0.92, warmth=0.45, formality=0.75, assertiveness=0.80
        ),
        speech=SpeechSpec(sentence_length="short", pace_multiplier=0.98, accent="british_received"),
        topics=TopicsSpec(allowed=["investor_updates", "security_compliance", "board_reports"], restricted=["speculative_guidance"]),
        gesture_profile=GestureProfile(expressiveness=0.50, gesture_library="keynote_authority"),
        brand=BrandBinding(org_id="example_co"),
        rights_ref="rights://david/auth-2026"
    ).seal()

    nova = DigitalDNA(
        character_id="nova",
        version="1.4.0",
        status="active",
        identity=IdentitySpec(
            face_embedding_ref="vault://identity/nova/face-v1.emb",
            voice_model_id="nova-youth-v1"
        ),
        personality_vector=PersonalityVector(
            confident=0.70, witty=0.85, analytical=0.60, warmth=0.90, formality=0.20, assertiveness=0.50
        ),
        speech=SpeechSpec(sentence_length="short", pace_multiplier=1.10, accent="california_casual"),
        topics=TopicsSpec(allowed=["developer_onboarding", "coding_tutorials", "hackathons"], restricted=["financial_advice"]),
        gesture_profile=GestureProfile(expressiveness=0.90, gesture_library="animated_enthusiastic"),
        brand=BrandBinding(org_id="example_co"),
        rights_ref="rights://nova/auth-2026"
    ).seal()

    maya_rights = RightsRecord(
        rights_id="rights-maya-2026-04",
        character_id="maya",
        likeness_holder="Maya Sharma & Antigravity Studio Labs",
        consent_scope=["marketing", "product_education", "social_distribution", "interactive_live"],
        consent_excludes=["political", "financial_endorsement", "adult_content"],
        territories=["IN", "US", "global_digital"],
        expiration="2027-04-01",
        revocable=True,
        signature="vault-signed:ed25519:7a4c9e81b2f3456d90e87123aa44ccbb",
        renewal_status="active"
    )

    return {
        "characters": {
            "maya": maya_1_7,
            "maya_v1_0": maya_1_0,
            "aria": aria,
            "david": david,
            "nova": nova
        },
        "rights": {
            "maya": maya_rights
        }
    }
