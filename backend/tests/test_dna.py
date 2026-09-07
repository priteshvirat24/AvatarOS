import pytest
from backend.app.models.dna import (
    DigitalDNA, IdentitySpec, PersonalityVector, SpeechSpec,
    TopicsSpec, GestureProfile, BrandBinding, validate_dna_write_guard
)

def test_dna_sealing_and_checksum():
    dna = DigitalDNA(
        character_id="test_char",
        version="1.0.0",
        identity=IdentitySpec(
            face_embedding_ref="vault://identity/test.emb",
            voice_model_id="test-voice-v1"
        ),
        personality_vector=PersonalityVector(),
        speech=SpeechSpec(),
        topics=TopicsSpec(allowed=["tech"], restricted=["politics"]),
        gesture_profile=GestureProfile(),
        brand=BrandBinding(),
        rights_ref="rights://test/2026"
    )
    assert dna.checksum is None
    dna.seal()
    assert dna.checksum is not None
    assert dna.checksum.startswith("sha256:")

def test_write_guard_rejection():
    dna = DigitalDNA(
        character_id="test_char",
        identity=IdentitySpec(face_embedding_ref="vault://1", voice_model_id="v1"),
        personality_vector=PersonalityVector(),
        speech=SpeechSpec(),
        topics=TopicsSpec(),
        gesture_profile=GestureProfile(),
        brand=BrandBinding(),
        rights_ref="rights://1"
    )
    
    # Non-admin attempting to touch identity must raise PermissionError
    with pytest.raises(PermissionError):
        validate_dna_write_guard(dna, caller_role="script_agent", changes={"identity.face_embedding_ref": "vault://hacked"})

    with pytest.raises(PermissionError):
        validate_dna_write_guard(dna, caller_role="evolution_agent", changes={"rights_ref": "rights://bypass"})

    # Human admin is allowed
    assert validate_dna_write_guard(dna, caller_role="human_admin", changes={"identity.face_embedding_ref": "vault://new"}) is True
